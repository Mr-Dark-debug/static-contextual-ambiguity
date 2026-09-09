from functools import lru_cache

import numpy as np
import pytest
from transformers import AutoTokenizer, PreTrainedTokenizerBase

from lexical_ambiguity.embeddings.bert import (
    BertAlignmentError,
    overlapping_token_indices,
    pool_subwords,
)

MODEL = "google-bert/bert-base-uncased"
REVISION = "f584a14f45f850d60d0036d54f3e4dfdb3d52075"


@lru_cache(maxsize=1)
def tokenizer() -> PreTrainedTokenizerBase:
    loaded = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, use_fast=True)
    assert loaded.is_fast
    return loaded


def aligned(sentence: str, start: int, end: int) -> tuple[list[int], list[tuple[int, int]]]:
    encoded = tokenizer()(sentence, return_offsets_mapping=True)
    offsets = [tuple(pair) for pair in encoded["offset_mapping"]]
    return list(overlapping_token_indices(offsets, start, end)), offsets


def test_alignment_ignores_special_tokens_and_uses_exact_repeated_target() -> None:
    sentence = "The bank closed, but the river bank remained."
    start = sentence.rindex("bank")

    indices, offsets = aligned(sentence, start, start + 4)

    assert len(indices) == 1
    assert offsets[indices[0]] == (start, start + 4)


def test_alignment_collects_every_wordpiece_for_marked_surface() -> None:
    sentence = "The result was unaffordable."
    start = sentence.index("unaffordable")

    indices, offsets = aligned(sentence, start, start + len("unaffordable"))

    assert len(indices) > 1
    assert offsets[indices[0]][0] == start
    assert offsets[indices[-1]][1] == start + len("unaffordable")


def test_pool_subwords_means_only_aligned_rows() -> None:
    hidden = np.array([[1.0, 2.0], [3.0, 4.0], [9.0, 9.0]], dtype=np.float32)

    pooled = pool_subwords(hidden, (0, 1))

    np.testing.assert_allclose(pooled, [2.0, 3.0])


def test_missing_alignment_fails_instead_of_guessing() -> None:
    with pytest.raises(BertAlignmentError, match="overlaps"):
        overlapping_token_indices([(0, 0), (0, 3), (4, 8), (0, 0)], 9, 12)
