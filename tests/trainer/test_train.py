import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "python" / "trainer"))

from train import WINDOW_IN, WINDOW_OUT, _next_version, create_windows


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
        blob1.name = "models/xgb_v3.pkl"
        blob2 = mocker.MagicMock()
        blob2.name = "models/xgb_v1.pkl"
        client.list_blobs.return_value = [blob1, blob2]
        assert _next_version(client) == 4
