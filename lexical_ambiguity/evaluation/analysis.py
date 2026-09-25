"""Deterministic partitions for quantitative and qualitative error analysis."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray


def outcome_partitions(
    frame: pd.DataFrame,
    *,
    static_correct: str,
    bert_correct: str,
    all_correct_columns: Sequence[str],
) -> NDArray[np.str_]:
    """Assign each row to exactly one system-agreement partition."""

    required = {static_correct, bert_correct, *all_correct_columns}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"prediction frame is missing columns: {sorted(missing)}")
    static = frame[static_correct].astype(bool).to_numpy()
    bert = frame[bert_correct].astype(bool).to_numpy()
    all_wrong = ~frame[list(all_correct_columns)].astype(bool).any(axis=1).to_numpy()
    output = np.full(len(frame), "both_primary_wrong", dtype="U24")
    output[static & bert] = "both_primary_correct"
    output[~static & bert] = "bert_only_correct"
    output[static & ~bert] = "static_only_correct"
    output[all_wrong] = "all_wrong"
    return output


def error_focus_partitions(
    scores: ArrayLike,
    labels: ArrayLike,
    *,
    threshold: float,
    borderline_width: float = 0.025,
    high_confidence_quantile: float = 0.75,
) -> NDArray[np.str_]:
    """Partition one system's errors by distance from its frozen threshold."""

    score_array = np.asarray(scores, dtype=np.float64)
    label_array = np.asarray(labels, dtype=np.bool_)
    if score_array.ndim != 1 or score_array.shape != label_array.shape:
        raise ValueError("scores and labels must be equal-length one-dimensional arrays")
    if not np.isfinite(score_array).all() or not np.isfinite(threshold):
        raise ValueError("scores and threshold must be finite")
    if borderline_width < 0.0 or not 0.0 < high_confidence_quantile < 1.0:
        raise ValueError("invalid error-partition parameters")
    errors = (score_array >= threshold) != label_array
    margins = np.abs(score_array - threshold)
    output = np.full(len(score_array), "correct", dtype="U24")
    if not errors.any():
        return output
    cutoff = float(np.quantile(margins[errors], high_confidence_quantile))
    output[errors] = "other_error"
    output[errors & (margins >= cutoff)] = "high_confidence_error"
    # Borderline has explicit precedence if a tiny dataset makes cutoffs cross.
    output[errors & (margins <= borderline_width)] = "borderline_error"
    return output


def summarize_boolean_group(
    frame: pd.DataFrame, *, group_column: str, value_column: str
) -> list[dict[str, object]]:
    """Return count and mean for a boolean outcome grouped by a saved feature."""

    if group_column not in frame or value_column not in frame:
        raise ValueError("summary columns are missing")
    grouped = frame.groupby(group_column, dropna=False)[value_column]
    return [
        {
            group_column: str(group),
            "count": int(values.count()),
            "mean": float(values.astype(bool).mean()),
        }
        for group, values in grouped
    ]

