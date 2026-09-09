import numpy as np

from lexical_ambiguity.evaluation.metrics import evaluate_scores


def test_metrics_use_true_as_positive_and_fixed_confusion_order() -> None:
    labels = np.array([False, False, True, True])
    scores = np.array([0.1, 0.7, 0.8, 0.4])

    metrics = evaluate_scores(scores, labels, threshold=0.5)

    assert metrics.accuracy == 0.5
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.confusion_matrix == ((1, 1), (1, 1))
    assert metrics.roc_auc == 0.75


def test_constant_scores_have_chance_roc_auc() -> None:
    metrics = evaluate_scores(
        np.ones(4),
        np.array([False, False, True, True]),
        threshold=0.5,
    )

    assert metrics.roc_auc == 0.5
