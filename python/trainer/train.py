import io
import os
import re

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from azure.storage.blob import BlobServiceClient, ContainerClient
from torch.utils.data import DataLoader, TensorDataset

from model import LSTMModel

WINDOW_IN = 30
WINDOW_OUT = 14
EPOCHS = 50
BATCH_SIZE = 16
LR = 1e-3


def _container_client() -> ContainerClient:
    conn_str = os.environ["AZURE_STORAGE_CONN_STR"]
    container = os.environ["BLOB_CONTAINER"]
    return BlobServiceClient.from_connection_string(conn_str).get_container_client(container)


def download_raw_data(client: ContainerClient) -> pd.DataFrame:
    blob = client.get_blob_client("raw/brussels.csv")
    data = blob.download_blob().readall()
    return pd.read_csv(io.BytesIO(data), parse_dates=["date"])


def create_windows(
    values: np.ndarray, window_in: int, window_out: int
) -> tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for i in range(len(values) - window_in - window_out + 1):
        X.append(values[i : i + window_in])
        y.append(values[i + window_in : i + window_in + window_out])
    return np.array(X), np.array(y)


def _next_version(client: ContainerClient) -> int:
    blobs = [b.name for b in client.list_blobs(name_starts_with="models/lstm_v")]
    if not blobs:
        return 1
    versions = [int(m.group(1)) for b in blobs if (m := re.search(r"lstm_v(\d+)\.pt$", b))]
    return max(versions) + 1 if versions else 1


def train(client: ContainerClient) -> None:
    df = download_raw_data(client)
    raw = df["temperature"].values.astype(np.float32)

    scaler_min = float(raw.min())
    scaler_max = float(raw.max())
    normalized = (raw - scaler_min) / (scaler_max - scaler_min)

    X, y = create_windows(normalized, WINDOW_IN, WINDOW_OUT)
    X_t = torch.tensor(X).unsqueeze(-1)
    y_t = torch.tensor(y)

    loader = DataLoader(TensorDataset(X_t, y_t), batch_size=BATCH_SIZE, shuffle=True)

    model = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0.0
        for xb, yb in loader:
            optimizer.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{EPOCHS} — loss: {total_loss / len(loader):.6f}")

    version = _next_version(client)
    buf = io.BytesIO()
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "scaler_min": scaler_min,
            "scaler_max": scaler_max,
            "version": version,
        },
        buf,
    )
    buf.seek(0)
    client.upload_blob(f"models/lstm_v{version}.pt", buf, overwrite=True)
    print(f"Model uploaded as models/lstm_v{version}.pt")


if __name__ == "__main__":
    train(_container_client())
