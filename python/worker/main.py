import io
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import joblib
import numpy as np
from azure.storage.blob import BlobServiceClient, ContainerClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

WINDOW_IN = 30


class PredictRequest(BaseModel):
    features: list[float]


class PredictResponse(BaseModel):
    forecast: list[float]


_model = None
_scaler_min: float = 0.0
_scaler_max: float = 1.0


def _container_client() -> ContainerClient:
    conn_str = os.environ["AZURE_STORAGE_CONN_STR"]
    container = os.environ["BLOB_CONTAINER"]
    return BlobServiceClient.from_connection_string(conn_str).get_container_client(container)


def _latest_model_blob(client: ContainerClient) -> str:
    blobs = sorted(
        [b.name for b in client.list_blobs(name_starts_with="models/xgb_v")],
        key=lambda n: int(n.split("_v")[1].replace(".pkl", "")),
    )
    if not blobs:
        raise RuntimeError("No model found in blob storage")
    return blobs[-1]


def load_model() -> None:
    global _model, _scaler_min, _scaler_max
    client = _container_client()
    blob_name = _latest_model_blob(client)
    data = client.get_blob_client(blob_name).download_blob().readall()
    artifact = joblib.load(io.BytesIO(data))
    _model = artifact["model"]
    _scaler_min = artifact["scaler_min"]
    _scaler_max = artifact["scaler_max"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    load_model()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if len(request.features) != WINDOW_IN:
        raise HTTPException(
            status_code=422,
            detail=f"Expected {WINDOW_IN} features, got {len(request.features)}",
        )

    raw = np.array(request.features, dtype=np.float32)
    normalized = (raw - _scaler_min) / (_scaler_max - _scaler_min)
    pred = _model.predict(normalized.reshape(1, -1))[0]
    forecast = (pred * (_scaler_max - _scaler_min) + _scaler_min).tolist()
    return PredictResponse(forecast=forecast)


@app.post("/reload", status_code=204)
def reload() -> None:
    load_model()
