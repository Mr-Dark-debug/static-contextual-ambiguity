"""Similarity functions with checks that turn silent numerical bugs into errors."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


class SimilarityError(ValueError):
    """Raised when similarity inputs are not valid finite vectors."""


def cosine_similarity(first: ArrayLike, second: ArrayLike) -> float:
    a = np.asarray(first, dtype=np.float64)
    b = np.asarray(second, dtype=np.float64)
    if a.ndim != 1 or b.ndim != 1 or a.shape != b.shape:
        raise SimilarityError(
            f"vectors must have the same one-dimensional shape: {a.shape}, {b.shape}"
        )
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise SimilarityError("vectors must contain only finite values")
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0.0:
        raise SimilarityError("cosine similarity is undefined for a zero vector")
    # Numerical noise can otherwise produce values a few ulps outside [-1, 1].
    return float(np.clip(np.dot(a, b) / denominator, -1.0, 1.0))
