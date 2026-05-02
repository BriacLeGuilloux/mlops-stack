import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import joblib
import numpy as np
import pytest
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

sys.path.insert(0, str(Path(__file__).parents[2] / "python" / "worker"))


def _make_artifact() -> dict:
    X = np.random.rand(20, 30).astype(np.float32)
    y = np.random.rand(20, 14).astype(np.float32)
    model = MultiOutputRegressor(XGBRegressor(n_estimators=5))
    model.fit(X, y)
    return {"model": model, "scaler_min": -5.0, "scaler_max": 35.0, "version": 1}


@pytest.fixture()
def client_with_model():
    import main as worker_main

    artifact = _make_artifact()
    buf = io.BytesIO()
    joblib.dump(artifact, buf)
    buf.seek(0)
    model_bytes = buf.read()

    blob_client = MagicMock()
    blob_client.download_blob.return_value.readall.return_value = model_bytes

    container_client = MagicMock()
    container_client.list_blobs.return_value = [MagicMock(name="models/xgb_v1.pkl")]
    container_client.get_blob_client.return_value = blob_client

    with patch.object(worker_main, "_container_client", return_value=container_client):
        worker_main.load_model()

    from fastapi.testclient import TestClient

    with TestClient(worker_main.app, raise_server_exceptions=True) as c:
        yield c, worker_main


class TestPredict:
    def test_valid_request(self, client_with_model) -> None:
        client, _ = client_with_model
        features = [float(i) for i in range(30)]
        resp = client.post("/predict", json={"features": features})
        assert resp.status_code == 200
        body = resp.json()
        assert "forecast" in body
        assert len(body["forecast"]) == 14

    def test_wrong_feature_count(self, client_with_model) -> None:
        client, _ = client_with_model
        resp = client.post("/predict", json={"features": [1.0, 2.0]})
        assert resp.status_code == 422

    def test_forecast_is_denormalized(self, client_with_model) -> None:
        client, _ = client_with_model
        features = [15.0] * 30
        resp = client.post("/predict", json={"features": features})
        assert resp.status_code == 200


class TestReload:
    def test_reload_returns_204(self, client_with_model, mocker) -> None:
        client, worker_main = client_with_model
        artifact = _make_artifact()
        buf = io.BytesIO()
        joblib.dump(artifact, buf)
        buf.seek(0)

        blob_client = MagicMock()
        blob_client.download_blob.return_value.readall.return_value = buf.read()
        container_client = MagicMock()
        container_client.list_blobs.return_value = [MagicMock(name="models/xgb_v2.pkl")]
        container_client.get_blob_client.return_value = blob_client

        mocker.patch.object(worker_main, "_container_client", return_value=container_client)
        resp = client.post("/reload")
        assert resp.status_code == 204
