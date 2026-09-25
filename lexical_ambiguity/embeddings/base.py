"""The small contract our embedding methods have in common.

Each method takes one WiC example and chooses the marked word in either
sentence. The experiment can then compare two vectors without knowing how
GloVe or BERT produced them.
"""

from __future__ import annotations

from typing import Protocol

from numpy.typing import NDArray

from lexical_ambiguity.types import Side, WicExample

Vector = NDArray


class TargetEncoder(Protocol):
    """Describe an encoder's shape; this class does not train or load a model."""

    def encode(self, example: WicExample, side: Side) -> Vector | None:
        """Encode one marked target occurrence."""

        ...
