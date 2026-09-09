import numpy as np
import pytest

from lexical_ambiguity.evaluation.metrics import evaluate_scores
from lexical_ambiguity.evaluation.threshold import (
    make_tuning_split,
    select_threshold,
    threshold_candidates,
)


def test_threshold_is_fit_in_gap_and_uses_positive_high_direction() -> None:
    result = select_threshold(
        np.array([0.1, 0.2, 0.8, 0.9]),
        np.array([False, False, True, True]),
    )

    assert 0.2 < result.threshold < 0.8
    assert result.macro_f1 == 1.0


def test_constant_scores_have_deterministic_all_positive_tie_break() -> None:
    result = select_threshold(np.ones(4), np.array([False, False, True, True]))

    assert result.threshold < 1.0
    assert result.macro_f1 == 1.0 / 3.0


def test_tuning_split_is_stratified_and_reproducible() -> None:
    labels = np.array([False, True] * 50)

    train_a, holdout_a = make_tuning_split(labels, holdout_fraction=0.2, seed=2026)
    train_b, holdout_b = make_tuning_split(labels, holdout_fraction=0.2, seed=2026)

    np.testing.assert_array_equal(train_a, train_b)
    np.testing.assert_array_equal(holdout_a, holdout_b)
    assert labels[train_a].sum() == 40
    assert labels[holdout_a].sum() == 10


def test_sorted_sweep_matches_brute_force_threshold_selection() -> None:
    generator = np.random.default_rng(19)
    scores = np.round(generator.uniform(-1.0, 1.0, size=80), 2)
    labels = generator.integers(0, 2, size=80).astype(bool)
    brute = []
    for threshold in threshold_candidates(scores):
        metrics = evaluate_scores(scores, labels, threshold)
        brute.append(
            (
                (
                    metrics.macro_f1,
                    metrics.accuracy,
                    -abs(float(threshold) - 0.5),
                    -float(threshold),
                ),
                float(threshold),
                metrics,
            )
        )
    _, threshold, metrics = max(brute, key=lambda item: item[0])

    swept = select_threshold(scores, labels)

    assert swept.threshold == threshold
    assert swept.macro_f1 == pytest.approx(metrics.macro_f1)
    assert swept.accuracy == pytest.approx(metrics.accuracy)
    assert swept.roc_auc == pytest.approx(metrics.roc_auc)
