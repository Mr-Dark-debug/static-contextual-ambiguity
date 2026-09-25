"""Metric computation with the WiC positive label fixed to same-sense=True."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


class MetricError(ValueError):
    """Raised for invalid score/label arrays."""


@dataclass(frozen=True, slots=True)
class MetricSet:
    accuracy: float
    macro_f1: float
    precision: float
    recall: float
    roc_auc: float
    confusion_matrix: tuple[tuple[int, int], tuple[int, int]]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def checked_arrays(scores: ArrayLike, labels: ArrayLike) -> tuple[NDArray, NDArray]:
    score_array = np.asarray(scores, dtype=np.float64)
    label_array = np.asarray(labels)
    if score_array.ndim != 1 or label_array.ndim != 1:
        raise MetricError("scores and labels must be one-dimensional")
    if len(score_array) == 0 or len(score_array) != len(label_array):
        raise MetricError("scores and labels must be non-empty and have equal length")
    if not np.isfinite(score_array).all():
        raise MetricError("scores contain non-finite values")
    unique_labels = set(label_array.tolist())
    if not unique_labels <= {False, True}:
        raise MetricError(f"labels must be boolean; got {sorted(unique_labels, key=str)}")
    return score_array, label_array.astype(bool)


def evaluate_scores(scores: ArrayLike, labels: ArrayLike, threshold: float) -> MetricSet:
    score_array, label_array = checked_arrays(scores, labels)
    if not np.isfinite(threshold):
        raise MetricError("threshold must be finite")
    predictions = score_array >= threshold
    matrix = confusion_matrix(label_array, predictions, labels=[False, True])
    if len(np.unique(label_array)) == 2:
        roc_auc = float(roc_auc_score(label_array, score_array))
    else:
        roc_auc = float("nan")
    return MetricSet(
        accuracy=float(accuracy_score(label_array, predictions)),
        macro_f1=float(f1_score(label_array, predictions, average="macro", zero_division=0)),
        precision=float(precision_score(label_array, predictions, pos_label=True, zero_division=0)),
        recall=float(recall_score(label_array, predictions, pos_label=True, zero_division=0)),
        roc_auc=roc_auc,
        confusion_matrix=(
            (int(matrix[0, 0]), int(matrix[0, 1])),
            (int(matrix[1, 0]), int(matrix[1, 1])),
        ),
        count=len(label_array),
    )
