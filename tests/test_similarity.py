import numpy as np
import pytest

from lexical_ambiguity.evaluation.similarity import SimilarityError, cosine_similarity


def test_cosine_similarity_matches_geometry() -> None:
    assert cosine_similarity(np.array([1.0, 0.0]), np.array([1.0, 0.0])) == pytest.approx(1.0)
    assert cosine_similarity(np.array([1.0, 0.0]), np.array([0.0, 1.0])) == pytest.approx(0.0)


def test_cosine_similarity_rejects_zero_and_mismatched_vectors() -> None:
    with pytest.raises(SimilarityError, match="zero"):
        cosine_similarity(np.zeros(2), np.ones(2))
    with pytest.raises(SimilarityError, match="shape"):
        cosine_similarity(np.ones(2), np.ones(3))
