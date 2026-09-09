from pathlib import Path

import numpy as np

from lexical_ambiguity.embeddings.glove import (
    EmbeddingStore,
    StaticContextEncoder,
    StaticTargetEncoder,
    context_tokens,
)
from lexical_ambiguity.types import WicExample


def example(
    *,
    sentence1: str = "The bank approved the loan.",
    start1: int = 4,
    end1: int = 8,
    sentence2: str = "We sat on the bank.",
    start2: int = 14,
    end2: int = 18,
    word: str = "bank",
) -> WicExample:
    return WicExample(
        idx=1,
        word=word,
        sentence1=sentence1,
        sentence2=sentence2,
        start1=start1,
        end1=end1,
        start2=start2,
        end2=end2,
        label=False,
        version="1.1",
        split="train",
    )


def store() -> EmbeddingStore:
    return EmbeddingStore(
        {
            "bank": np.array([1.0, 0.0, 0.0]),
            "the": np.array([0.0, 1.0, 0.0]),
            "approved": np.array([0.0, 0.0, 1.0]),
            "loan": np.array([1.0, 1.0, 0.0]),
            "old": np.array([1.0, 0.0, 1.0]),
            "collapsed": np.array([0.0, 1.0, 1.0]),
        },
        dimensions=3,
    )


def test_lookup_is_case_normalized_and_oov_is_none() -> None:
    vectors = store()

    np.testing.assert_array_equal(vectors.lookup("BANK"), [1.0, 0.0, 0.0])
    assert vectors.lookup("missing") is None


def test_from_text_streams_only_requested_vocabulary(tmp_path: Path) -> None:
    path = tmp_path / "tiny.txt"
    path.write_text("bank 1 0 0\nriver 0 1 0\nskip 0 0 1\n", encoding="utf-8")

    vectors = EmbeddingStore.from_text(path, dimensions=3, vocabulary={"bank", "river"})

    assert len(vectors) == 2
    assert vectors.lookup("skip") is None


def test_store_has_stable_pickle_free_cache_arrays() -> None:
    tokens, vectors = store().to_arrays()

    assert tokens.dtype.kind == "U"
    assert tokens.tolist() == sorted(tokens.tolist())
    assert vectors.shape == (len(tokens), 3)


def test_static_target_is_identical_across_inflected_surfaces() -> None:
    item = example(
        sentence1="They banked the fire.",
        start1=5,
        end1=11,
        sentence2="She is banking the plane.",
        start2=7,
        end2=14,
    )
    encoder = StaticTargetEncoder(store())

    np.testing.assert_array_equal(encoder.encode(item, 1), encoder.encode(item, 2))


def test_context_tokens_exclude_exact_repeated_target() -> None:
    sentence = "The bank sold the old bank building."
    marked = sentence.rindex("bank")
    item = example(sentence1=sentence, start1=marked, end1=marked + 4)

    tokens = context_tokens(item, side=1, window=2)

    assert [token.text for token in tokens] == ["the", "old", "building"]


def test_context_tokenization_handles_punctuation_and_contractions() -> None:
    sentence = "Don't bank—seriously—on luck."
    marked = sentence.index("bank")
    item = example(sentence1=sentence, start1=marked, end1=marked + 4)

    tokens = context_tokens(item, side=1, window="sentence")

    assert [token.text for token in tokens] == ["Don't", "seriously", "on", "luck"]


def test_static_context_averages_in_vocab_words_and_counts_oov() -> None:
    encoder = StaticContextEncoder(store(), window="sentence")

    encoded = encoder.encode(example(), 1)

    expected = np.mean(
        [
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([1.0, 1.0, 0.0]),
        ],
        axis=0,
    )
    np.testing.assert_allclose(encoded.vector, expected)
    assert encoded.used_tokens == ("the", "approved", "the", "loan")
    assert encoded.oov_count == 0
    assert encoded.used_target_fallback is False


def test_static_context_falls_back_to_target_when_context_is_all_oov() -> None:
    item = example(sentence1="Blurp bank zorp.", start1=6, end1=10)
    encoder = StaticContextEncoder(store(), window=2)

    encoded = encoder.encode(item, 1)

    np.testing.assert_array_equal(encoded.vector, [1.0, 0.0, 0.0])
    assert encoded.used_tokens == ()
    assert encoded.oov_count == 2
    assert encoded.used_target_fallback is True


def test_static_context_returns_missing_when_context_and_target_are_oov() -> None:
    item = example(
        sentence1="Blurp quux zorp.",
        start1=6,
        end1=10,
        word="quux",
    )
    encoder = StaticContextEncoder(store(), window=2)

    encoded = encoder.encode(item, 1)

    assert encoded.vector is None
    assert encoded.used_target_fallback is True
