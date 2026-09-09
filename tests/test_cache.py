from pathlib import Path

import numpy as np

from lexical_ambiguity.utils import load_array_cache, save_array_cache


def test_array_cache_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "vectors.npz"
    arrays = {"layer_1": np.arange(12, dtype=np.float32).reshape(2, 2, 3)}
    metadata = {"schema": 1, "model": "tiny", "ids": [1, 2]}

    save_array_cache(path, arrays, metadata)
    loaded = load_array_cache(path, metadata)

    assert loaded is not None
    np.testing.assert_array_equal(loaded["layer_1"], arrays["layer_1"])


def test_array_cache_miss_when_metadata_changes(tmp_path: Path) -> None:
    path = tmp_path / "vectors.npz"
    save_array_cache(path, {"x": np.ones(2)}, {"revision": "old"})

    assert load_array_cache(path, {"revision": "new"}) is None


def test_array_cache_miss_when_payload_is_corrupt(tmp_path: Path) -> None:
    path = tmp_path / "vectors.npz"
    save_array_cache(path, {"x": np.ones(2)}, {"revision": "same"})
    path.write_bytes(b"cursed cache")

    assert load_array_cache(path, {"revision": "same"}) is None
