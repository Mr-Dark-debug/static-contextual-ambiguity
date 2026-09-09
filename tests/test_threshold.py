import numpy as np

from lexical_ambiguity.evaluation.threshold import make_tuning_split, select_threshold


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
