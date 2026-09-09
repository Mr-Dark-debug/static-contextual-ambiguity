import numpy as np
import pandas as pd

from lexical_ambiguity.evaluation.analysis import (
    error_focus_partitions,
    outcome_partitions,
    summarize_boolean_group,
)


def test_outcome_partitions_are_disjoint_and_cover_expected_cases() -> None:
    frame = pd.DataFrame(
        {
            "target_correct": [False, False, False, True, True],
            "static_correct": [False, False, True, True, False],
            "bert_correct": [False, True, False, True, False],
        }
    )

    partitions = outcome_partitions(
        frame,
        static_correct="static_correct",
        bert_correct="bert_correct",
        all_correct_columns=("target_correct", "static_correct", "bert_correct"),
    )

    assert partitions.tolist() == [
        "all_wrong",
        "bert_only_correct",
        "static_only_correct",
        "both_primary_correct",
        "both_primary_wrong",
    ]


def test_error_focus_marks_borderline_and_high_confidence_errors() -> None:
    scores = np.array([0.49, 0.9, 0.1, 0.8, 0.2])
    labels = np.array([True, False, False, True, True])

    partitions = error_focus_partitions(
        scores,
        labels,
        threshold=0.5,
        borderline_width=0.02,
        high_confidence_quantile=0.5,
    )

    assert partitions[0] == "borderline_error"
    assert partitions[1] == "high_confidence_error"
    assert partitions[2] == "correct"
    assert partitions[3] == "correct"
    assert partitions[4] in {"other_error", "high_confidence_error"}


def test_boolean_group_summary_reports_counts_and_rates() -> None:
    frame = pd.DataFrame(
        {"surface_mismatch": [False, False, True], "correct": [True, False, False]}
    )

    rows = summarize_boolean_group(
        frame, group_column="surface_mismatch", value_column="correct"
    )

    assert rows == [
        {"surface_mismatch": "False", "count": 2, "mean": 0.5},
        {"surface_mismatch": "True", "count": 1, "mean": 0.0},
    ]

