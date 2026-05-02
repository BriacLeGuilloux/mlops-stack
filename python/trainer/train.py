import io
import os
import re

import joblib
import numpy as np
import pandas as pd
from azure.storage.blob import BlobServiceClient, ContainerClient
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

WINDOW_IN = 30
WINDOW_OUT = 14


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
    blobs = [b.name for b in client.list_blobs(name_starts_with="models/xgb_v")]
    if not blobs:
        return 1
    versions = [int(m.group(1)) for b in blobs if (m := re.search(r"xgb_v(\d+)\.pkl$", b))]
    return max(versions) + 1 if versions else 1


def train(client: ContainerClient) -> None:
    df = download_raw_data(client)
    raw = df["temperature"].values.astype(np.float32)

    scaler_min = float(raw.min())
    scaler_max = float(raw.max())
    normalized = (raw - scaler_min) / (scaler_max - scaler_min)

    X, y = create_windows(normalized, WINDOW_IN, WINDOW_OUT)

    model = MultiOutputRegressor(
        XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.1, n_jobs=-1)
    )
    model.fit(X, y)
    print("Training complete")

    version = _next_version(client)
    artifact = {"model": model, "scaler_min": scaler_min, "scaler_max": scaler_max, "version": version}

    buf = io.BytesIO()
    joblib.dump(artifact, buf)
    buf.seek(0)
    client.upload_blob(f"models/xgb_v{version}.pkl", buf, overwrite=True)
    print(f"Model uploaded as models/xgb_v{version}.pkl")


if __name__ == "__main__":
    train(_container_client())
