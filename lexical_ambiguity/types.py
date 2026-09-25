"""Small immutable records shared across the experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Side = Literal[1, 2]


@dataclass(frozen=True, slots=True)
class WicExample:
    """One Word-in-Context sentence pair with half-open character spans."""

    idx: int
    word: str
    sentence1: str
    sentence2: str
    start1: int
    end1: int
    start2: int
    end2: int
    label: bool | None
    version: str
    split: str

    def sentence(self, side: Side) -> str:
        return self.sentence1 if side == 1 else self.sentence2

    def target_span(self, side: Side) -> tuple[int, int]:
        return (self.start1, self.end1) if side == 1 else (self.start2, self.end2)

    def target_surface(self, side: Side) -> str:
        sentence = self.sentence(side)
        start, end = self.target_span(side)
        return sentence[start:end]


@dataclass(frozen=True, slots=True)
class DataAudit:
    split: str
    examples: int
    labeled: int
    positive: int
    negative: int
    unlabeled: int
    unique_words: int
    surface_lemma_mismatch: int
    repeated_surface_contexts: int
    symmetric_duplicate_pairs: int
    surface_contains_space: int
    empty_spans: int
    max_sentence_characters: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
