"""Shared embedding interfaces."""

from __future__ import annotations

from typing import Protocol

from numpy.typing import NDArray

from lexical_ambiguity.types import Side, WicExample

Vector = NDArray


class TargetEncoder(Protocol):
    def encode(self, example: WicExample, side: Side) -> Vector | None:
        """Encode one marked target occurrence."""

        ...
