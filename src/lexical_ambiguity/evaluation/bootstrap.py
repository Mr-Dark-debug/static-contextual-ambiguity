"""Paired non-parametric bootstrap intervals over WiC examples."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from lexical_ambiguity.evaluation.metrics import MetricSet, checked_arrays, evaluate_scores


@dataclass(frozen=True, slots=True)
class BootstrapInterval:
    system: str
    metric: str
    estimate: float
    lower: float
    upper: float
    confidence_level: float
    resamples: int


@dataclass(frozen=True, slots=True)
class PairedDifference:
    contrast: str
    metric: str
    estimate: float
    lower: float
    upper: float
    confidence_level: float
    resamples: int


_METRICS: dict[str, Callable[[MetricSet], float]] = {
    "accuracy": lambda metrics: metrics.accuracy,
    "macro_f1": lambda metrics: metrics.macro_f1,
    "roc_auc": lambda metrics: metrics.roc_auc,
}


def _bounds(values: list[float], confidence_level: float) -> tuple[float, float]:
    array = np.asarray(values, dtype=np.float64)
    alpha = 1.0 - confidence_level
    return (
        float(np.nanquantile(array, alpha / 2.0)),
        float(np.nanquantile(array, 1.0 - alpha / 2.0)),
    )


def _sample_indices(count: int, resamples: int, seed: int) -> list[NDArray[np.int64]]:
    if resamples <= 0:
        raise ValueError("resamples must be positive")
    generator = np.random.default_rng(seed)
    return [generator.integers(0, count, size=count) for _ in range(resamples)]


def bootstrap_intervals(
    score_sets: dict[str, ArrayLike],
    labels: ArrayLike,
    thresholds: dict[str, float],
    *,
    resamples: int,
    confidence_level: float,
    seed: int,
) -> list[BootstrapInterval]:
    if set(score_sets) != set(thresholds):
        raise ValueError("score sets and thresholds must name the same systems")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between zero and one")

    checked: dict[str, NDArray] = {}
    label_array: NDArray | None = None
    for name, scores in score_sets.items():
        score_array, current_labels = checked_arrays(scores, labels)
        checked[name] = score_array
        if label_array is None:
            label_array = current_labels
    if label_array is None:
        raise ValueError("at least one score set is required")

    samples = _sample_indices(len(label_array), resamples, seed)
    output: list[BootstrapInterval] = []
    for name in sorted(checked):
        point = evaluate_scores(checked[name], label_array, thresholds[name])
        bootstrap_values = {metric: [] for metric in _METRICS}
        for indices in samples:
            sampled = evaluate_scores(
                checked[name][indices], label_array[indices], thresholds[name]
            )
            for metric, getter in _METRICS.items():
                bootstrap_values[metric].append(getter(sampled))
        for metric, getter in _METRICS.items():
            lower, upper = _bounds(bootstrap_values[metric], confidence_level)
            output.append(
                BootstrapInterval(
                    system=name,
                    metric=metric,
                    estimate=getter(point),
                    lower=lower,
                    upper=upper,
                    confidence_level=confidence_level,
                    resamples=resamples,
                )
            )
    return output


def paired_differences(
    *,
    scores_a: ArrayLike,
    threshold_a: float,
    name_a: str,
    scores_b: ArrayLike,
    threshold_b: float,
    name_b: str,
    labels: ArrayLike,
    resamples: int,
    confidence_level: float,
    seed: int,
) -> list[PairedDifference]:
    first, label_array = checked_arrays(scores_a, labels)
    second, second_labels = checked_arrays(scores_b, labels)
    if len(first) != len(second) or not np.array_equal(label_array, second_labels):
        raise ValueError("paired systems must use the same labeled examples")
    point_a = evaluate_scores(first, label_array, threshold_a)
    point_b = evaluate_scores(second, label_array, threshold_b)
    differences = {metric: [] for metric in _METRICS}
    for indices in _sample_indices(len(label_array), resamples, seed):
        sampled_a = evaluate_scores(first[indices], label_array[indices], threshold_a)
        sampled_b = evaluate_scores(second[indices], label_array[indices], threshold_b)
        for metric, getter in _METRICS.items():
            differences[metric].append(getter(sampled_a) - getter(sampled_b))

    output: list[PairedDifference] = []
    for metric, getter in _METRICS.items():
        lower, upper = _bounds(differences[metric], confidence_level)
        output.append(
            PairedDifference(
                contrast=f"{name_a} - {name_b}",
                metric=metric,
                estimate=getter(point_a) - getter(point_b),
                lower=lower,
                upper=upper,
                confidence_level=confidence_level,
                resamples=resamples,
            )
        )
    return output
