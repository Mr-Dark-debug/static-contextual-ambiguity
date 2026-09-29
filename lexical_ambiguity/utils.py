"""Reproducibility, provenance, atomic writes, and cache helpers."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import subprocess
import tempfile
import zipfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import torch
import transformers
from numpy.typing import NDArray

from lexical_ambiguity.types import WicExample

CACHE_SCHEMA_VERSION = 1


def canonical_hash(payload: Any) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def fingerprint_examples(examples: list[WicExample]) -> str:
    fields = [
        (
            item.split,
            item.idx,
            item.word,
            item.sentence1,
            item.start1,
            item.end1,
            item.sentence2,
            item.start2,
            item.end2,
            item.label,
        )
        for item in examples
    ]
    return canonical_hash(fields)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f"{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")


def _metadata_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".json")


def save_array_cache(
    path: Path,
    arrays: Mapping[str, NDArray],
    metadata: Mapping[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w+b", prefix=f"{path.name}.", suffix=".tmp", dir=path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        np.savez_compressed(temporary, **arrays)
    temporary_path.replace(path)
    atomic_write_json(_metadata_path(path), dict(metadata))


def load_array_cache(path: Path, expected_metadata: Mapping[str, Any]) -> dict[str, NDArray] | None:
    metadata_path = _metadata_path(path)
    if not path.exists() or not metadata_path.exists():
        return None
    try:
        actual_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if actual_metadata != dict(expected_metadata):
            return None
        with np.load(path, allow_pickle=False) as bundle:
            return {name: bundle[name] for name in bundle.files}
    except (OSError, ValueError, EOFError, json.JSONDecodeError, zipfile.BadZipFile):
        return None


def set_global_seed(seed: int, *, deterministic: bool) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        warn_only = os.getenv("LEXICAL_AMBIGUITY_WARN_ONLY_DETERMINISM", "0") == "1"
        torch.use_deterministic_algorithms(True, warn_only=warn_only)
        torch.backends.cudnn.benchmark = False


def git_state(project_root: Path) -> dict[str, Any]:
    def run(*arguments: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", *arguments],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return result.stdout.strip()

    status = run("status", "--porcelain")
    return {
        "commit": run("rev-parse", "HEAD"),
        "branch": run("branch", "--show-current"),
        "dirty": bool(status) if status is not None else None,
    }


def environment_info(project_root: Path) -> dict[str, Any]:
    cuda = torch.cuda.is_available()
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "numpy": np.__version__,
        "cuda_available": cuda,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if cuda else None,
        "git": git_state(project_root),
    }
