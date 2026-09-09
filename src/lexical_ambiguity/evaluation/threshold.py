"""Train-only threshold selection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from sklearn.model_selection import train_test_split

from lexical_ambiguity.evaluation.metrics import checked_arrays, evaluate_scores


@dataclass(frozen=True, slots=True)
class ThresholdSelection:
    threshold: float
    macro_f1: float
    accuracy: float
    roc_auc: float


def threshold_candidates(scores: ArrayLike) -> NDArray[np.float64]:
    values = np.unique(np.asarray(scores, dtype=np.float64))
    if values.ndim != 1 or len(values) == 0 or not np.isfinite(values).all():
        raise ValueError("threshold scores must be a non-empty finite vector")
    lower = np.nextafter(values[0], -np.inf)
    upper = np.nextafter(values[-1], np.inf)
    if len(values) == 1:
        return np.array([lower, upper], dtype=np.float64)
    midpoints = values[:-1] + (values[1:] - values[:-1]) / 2.0
    return np.concatenate(([lower], midpoints, [upper]))


def select_threshold(scores: ArrayLike, labels: ArrayLike) -> ThresholdSelection:
    score_array, label_array = checked_arrays(scores, labels)
    best_key: tuple[float, float, float, float] | None = None
    best: ThresholdSelection | None = None
    for threshold in threshold_candidates(score_array):
        metrics = evaluate_scores(score_array, label_array, float(threshold))
        key = (
            metrics.macro_f1,
            metrics.accuracy,
            -abs(float(threshold) - 0.5),
            -float(threshold),
        )
        if best_key is None or key > best_key:
            best_key = key
            best = ThresholdSelection(
                threshold=float(threshold),
                macro_f1=metrics.macro_f1,
                accuracy=metrics.accuracy,
                roc_auc=metrics.roc_auc,
            )
    assert best is not None  # checked_arrays rejects empty input
    return best


def make_tuning_split(
    labels: ArrayLike, *, holdout_fraction: float, seed: int
) -> tuple[NDArray[np.int64], NDArray[np.int64]]:
    label_array = np.asarray(labels).astype(bool)
    if label_array.ndim != 1 or len(label_array) < 4:
        raise ValueError("at least four one-dimensional labels are required")
    if not 0.0 < holdout_fraction < 0.5:
        raise ValueError("holdout_fraction must be between 0 and 0.5")
    indices = np.arange(len(label_array), dtype=np.int64)
    train_indices, holdout_indices = train_test_split(
        indices,
        test_size=holdout_fraction,
        random_state=seed,
        stratify=label_array,
    )
    return np.sort(train_indices), np.sort(holdout_indices)
