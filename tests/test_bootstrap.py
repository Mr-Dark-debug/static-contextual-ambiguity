import numpy as np

from lexical_ambiguity.evaluation.bootstrap import bootstrap_intervals, paired_differences


def test_bootstrap_is_reproducible_and_contains_point_estimate() -> None:
    labels = np.array([False, True] * 20)
    scores = np.linspace(0.0, 1.0, len(labels))
    thresholds = {"model": 0.5}

    first = bootstrap_intervals(
        {"model": scores}, labels, thresholds, resamples=100, confidence_level=0.95, seed=9
    )
    second = bootstrap_intervals(
        {"model": scores}, labels, thresholds, resamples=100, confidence_level=0.95, seed=9
    )

    assert first == second
    for interval in first:
        assert interval.lower <= interval.estimate <= interval.upper


def test_paired_identical_systems_have_zero_difference() -> None:
    labels = np.array([False, False, True, True] * 10)
    scores = np.array([0.1, 0.2, 0.8, 0.9] * 10)

    differences = paired_differences(
        scores_a=scores,
        threshold_a=0.5,
        name_a="a",
        scores_b=scores.copy(),
        threshold_b=0.5,
        name_b="b",
        labels=labels,
        resamples=100,
        confidence_level=0.95,
        seed=4,
    )

    assert all(item.estimate == 0.0 for item in differences)
    assert all(item.lower == 0.0 and item.upper == 0.0 for item in differences)
