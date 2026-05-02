import sys
from pathlib import Path

import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).parents[2] / "python" / "trainer"))

from model import LSTMModel
from train import WINDOW_IN, WINDOW_OUT, _next_version, create_windows


class TestLSTMModel:
    def test_output_shape(self) -> None:
        model = LSTMModel()
        x = torch.randn(4, WINDOW_IN, 1)
        out = model(x)
        assert out.shape == (4, WINDOW_OUT)

    def test_default_hyperparams(self) -> None:
        model = LSTMModel()
        assert model.fc.out_features == 14
        assert model.fc.in_features == 64

    def test_single_sample(self) -> None:
        model = LSTMModel()
        x = torch.randn(1, WINDOW_IN, 1)
        out = model(x)
        assert out.shape == (1, 14)


class TestCreateWindows:
    def test_window_count(self) -> None:
        values = np.arange(60, dtype=np.float32)
        X, y = create_windows(values, WINDOW_IN, WINDOW_OUT)
        expected = 60 - WINDOW_IN - WINDOW_OUT + 1
        assert len(X) == expected
        assert len(y) == expected

    def test_window_shapes(self) -> None:
        values = np.arange(60, dtype=np.float32)
        X, y = create_windows(values, WINDOW_IN, WINDOW_OUT)
        assert X.shape[1] == WINDOW_IN
        assert y.shape[1] == WINDOW_OUT

    def test_window_values(self) -> None:
        values = np.arange(50, dtype=np.float32)
        X, y = create_windows(values, WINDOW_IN, WINDOW_OUT)
        np.testing.assert_array_equal(X[0], values[:WINDOW_IN])
        np.testing.assert_array_equal(y[0], values[WINDOW_IN : WINDOW_IN + WINDOW_OUT])

    def test_minimum_input_length(self) -> None:
        values = np.arange(WINDOW_IN + WINDOW_OUT, dtype=np.float32)
        X, y = create_windows(values, WINDOW_IN, WINDOW_OUT)
        assert len(X) == 1


class TestNextVersion:
    def test_no_existing_models(self, mocker) -> None:
        client = mocker.MagicMock()
        client.list_blobs.return_value = []
        assert _next_version(client) == 1

    def test_increments_version(self, mocker) -> None:
        client = mocker.MagicMock()
        blob1 = mocker.MagicMock()
        blob1.name = "models/lstm_v3.pt"
        blob2 = mocker.MagicMock()
        blob2.name = "models/lstm_v1.pt"
        client.list_blobs.return_value = [blob1, blob2]
        assert _next_version(client) == 4
