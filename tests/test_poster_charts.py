import pandas as pd
import pytest

from lexical_ambiguity.visualization.poster_charts import paired_outcome_data


def test_primary_outcomes_include_every_neither_correct_case() -> None:
    predictions = pd.DataFrame(
        {
            "bert_mean_last_four_correct": [True, True, False, False, False],
            "glove_context_2_correct": [True, False, True, False, False],
            "glove_target_correct": [True, False, False, True, False],
        }
    )
    data = paired_outcome_data(predictions)
    assert data["count"].tolist() == [1, 1, 1, 2]
    assert data["count"].sum() == len(predictions)
    assert data["count"].iloc[0] + data["count"].iloc[1] == predictions.iloc[:, 0].sum()
    assert data["count"].iloc[0] + data["count"].iloc[2] == predictions.iloc[:, 1].sum()


def test_outcomes_reject_string_booleans_instead_of_counting_false_as_true() -> None:
    predictions = pd.DataFrame(
        {
            "bert_mean_last_four_correct": ["False"],
            "glove_context_2_correct": ["True"],
        }
    )
    with pytest.raises(ValueError, match="boolean"):
        paired_outcome_data(predictions)
