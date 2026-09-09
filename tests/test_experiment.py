import numpy as np

from lexical_ambiguity.embeddings.glove import EmbeddingStore
from lexical_ambiguity.experiment import (
    _static_scores,
    choose_candidate,
    fill_missing_scores,
    pairwise_cosine_scores,
    stratified_limit,
)
from lexical_ambiguity.types import WicExample


def examples(count: int) -> list[WicExample]:
    return [
        WicExample(
            idx=index,
            word="bank",
            sentence1="The bank opened.",
            sentence2="The bank closed.",
            start1=4,
            end1=8,
            start2=4,
            end2=8,
            label=bool(index % 2),
            version="1.1",
            split="train",
        )
        for index in range(count)
    ]


def test_pairwise_cosine_scores_preserve_pair_order() -> None:
    vectors = np.array(
        [
            [[1.0, 0.0], [1.0, 0.0]],
            [[1.0, 0.0], [0.0, 1.0]],
        ]
    )

    np.testing.assert_allclose(pairwise_cosine_scores(vectors), [1.0, 0.0])


def test_stratified_limit_is_balanced_and_reproducible() -> None:
    rows = examples(100)

    first = stratified_limit(rows, 20, seed=7)
    second = stratified_limit(rows, 20, seed=7)

    assert [item.idx for item in first] == [item.idx for item in second]
    assert sum(item.label is True for item in first) == 10


def test_candidate_selection_uses_tune_threshold_and_holdout_metric() -> None:
    labels = np.array([False, True, False, True, False, True, False, True])
    good = np.array([0.1, 0.9, 0.2, 0.8, 0.15, 0.85, 0.25, 0.75])
    bad = 1.0 - good

    selected, records = choose_candidate(
        {"good": good, "bad": bad},
        labels,
        tune_indices=np.array([0, 1, 2, 3]),
        holdout_indices=np.array([4, 5, 6, 7]),
        simplicity_order=("bad", "good"),
    )

    assert selected == "good"
    assert {record.name for record in records} == {"good", "bad"}
    assert next(record for record in records if record.name == "good").holdout_macro_f1 == 1.0


def test_missing_scores_use_training_median_for_both_splits() -> None:
    train, validation, median = fill_missing_scores(
        np.array([0.2, np.nan, 0.8]), np.array([np.nan, 0.5])
    )

    assert median == 0.5
    np.testing.assert_allclose(train, [0.2, 0.5, 0.8])
    np.testing.assert_allclose(validation, [0.5, 0.5])


def test_static_target_diagnostic_is_exactly_constant() -> None:
    store = EmbeddingStore(
        {
            "bank": np.array([0.1, 0.3, 0.7]),
        },
        dimensions=3,
    )

    scores, _ = _static_scores(examples(2), store, windows=())

    np.testing.assert_array_equal(scores["glove_target"], [1.0, 1.0])
