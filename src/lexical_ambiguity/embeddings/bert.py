"""Offset-aligned target representations from frozen BERT hidden states."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import numpy as np
import torch
from numpy.typing import NDArray
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase

from lexical_ambiguity.config import BertConfig
from lexical_ambiguity.types import Side, WicExample


class BertAlignmentError(ValueError):
    """Raised when tokenizer offsets cannot identify the marked target."""


@dataclass(frozen=True, slots=True)
class BertRepresentations:
    vectors: dict[str, NDArray[np.float32]]
    wordpiece_counts: NDArray[np.int16]
    device: str
    model: str
    revision: str


def overlapping_token_indices(
    offsets: Sequence[Sequence[int]], target_start: int, target_end: int
) -> tuple[int, ...]:
    """Return tokens whose non-empty half-open spans overlap the target."""

    if target_start < 0 or target_end <= target_start:
        raise BertAlignmentError(f"invalid target span {target_start}:{target_end}")
    indices = tuple(
        index
        for index, pair in enumerate(offsets)
        if len(pair) == 2
        and int(pair[1]) > int(pair[0])
        and int(pair[1]) > target_start
        and int(pair[0]) < target_end
    )
    if not indices:
        raise BertAlignmentError(
            f"no tokenizer offset overlaps target span {target_start}:{target_end}"
        )
    return indices


def pool_subwords(hidden: NDArray, indices: Sequence[int]) -> NDArray[np.float32]:
    array = np.asarray(hidden, dtype=np.float32)
    if array.ndim != 2:
        raise BertAlignmentError(f"hidden states must be 2-D; got {array.shape}")
    if not indices:
        raise BertAlignmentError("cannot pool an empty WordPiece selection")
    if min(indices) < 0 or max(indices) >= array.shape[0]:
        raise BertAlignmentError("WordPiece index falls outside hidden-state rows")
    return np.mean(array[list(indices)], axis=0, dtype=np.float32)


def resolve_device(requested: str) -> torch.device:
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available")
        return torch.device("cuda")
    if requested == "auto" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class BertTargetEncoder:
    """Extract every BERT layer for both marked occurrences in one pass."""

    def __init__(
        self,
        config: BertConfig,
        *,
        device: str = "auto",
        tokenizer: PreTrainedTokenizerBase | None = None,
        model: PreTrainedModel | None = None,
    ) -> None:
        self.config = config
        self.device = resolve_device(device)
        self.tokenizer = tokenizer or AutoTokenizer.from_pretrained(
            config.model,
            revision=config.revision,
            use_fast=True,
        )
        if not self.tokenizer.is_fast:
            raise RuntimeError("BERT target alignment requires a fast tokenizer")
        self.model = model or AutoModel.from_pretrained(
            config.model,
            revision=config.revision,
            output_hidden_states=True,
        )
        self.model.to(self.device)
        self.model.eval()

    def _encode_batch(
        self, records: Sequence[tuple[WicExample, Side]]
    ) -> tuple[dict[str, list[NDArray[np.float32]]], list[int]]:
        sentences = [example.sentence(side) for example, side in records]
        encoded = self.tokenizer(
            sentences,
            padding=True,
            truncation=True,
            max_length=self.config.max_length,
            return_offsets_mapping=True,
            return_tensors="pt",
        )
        offset_mapping = encoded.pop("offset_mapping").cpu().numpy()
        model_inputs = {name: value.to(self.device) for name, value in encoded.items()}
        with torch.inference_mode():
            output = self.model(**model_inputs, output_hidden_states=True, return_dict=True)
        hidden_states = output.hidden_states
        if hidden_states is None or len(hidden_states) != 13:
            raise RuntimeError(
                f"expected embedding output plus 12 BERT layers; got "
                f"{0 if hidden_states is None else len(hidden_states)}"
            )

        vectors = {f"layer_{layer}": [] for layer in range(1, 13)}
        vectors["mean_last_four"] = []
        counts: list[int] = []
        for row, (example, side) in enumerate(records):
            start, end = example.target_span(side)
            try:
                indices = overlapping_token_indices(offset_mapping[row], start, end)
            except BertAlignmentError as error:
                surface = example.target_surface(side)
                raise BertAlignmentError(
                    f"{example.split}:{example.idx} side {side} surface={surface!r}: {error}"
                ) from error
            counts.append(len(indices))
            per_layer: list[torch.Tensor] = []
            tensor_indices = torch.as_tensor(indices, device=self.device)
            for layer in range(1, 13):
                pooled = hidden_states[layer][row].index_select(0, tensor_indices).mean(dim=0)
                per_layer.append(pooled)
                vectors[f"layer_{layer}"].append(
                    pooled.detach().to(dtype=torch.float32, device="cpu").numpy()
                )
            mean_last_four = torch.stack(per_layer[-4:]).mean(dim=0)
            vectors["mean_last_four"].append(
                mean_last_four.detach().to(dtype=torch.float32, device="cpu").numpy()
            )
        return vectors, counts

    def encode(
        self, examples: Iterable[WicExample], *, show_progress: bool = True
    ) -> BertRepresentations:
        rows = list(examples)
        if not rows:
            raise ValueError("cannot encode an empty example collection")
        records: list[tuple[WicExample, Side]] = [
            (example, side) for example in rows for side in (1, 2)
        ]
        collected = {f"layer_{layer}": [] for layer in range(1, 13)}
        collected["mean_last_four"] = []
        counts: list[int] = []

        cursor = 0
        batch_size = self.config.batch_size
        progress = tqdm(
            total=len(records),
            desc=f"BERT on {self.device.type}",
            disable=not show_progress,
        )
        try:
            while cursor < len(records):
                current = records[cursor : cursor + batch_size]
                try:
                    batch_vectors, batch_counts = self._encode_batch(current)
                except torch.cuda.OutOfMemoryError:
                    if self.device.type != "cuda" or batch_size == 1:
                        raise
                    torch.cuda.empty_cache()
                    batch_size = max(1, batch_size // 2)
                    continue
                for key, vectors in batch_vectors.items():
                    collected[key].extend(vectors)
                counts.extend(batch_counts)
                cursor += len(current)
                progress.update(len(current))
        finally:
            progress.close()

        stacked = {
            key: np.stack(vectors).astype(np.float32, copy=False).reshape(len(rows), 2, -1)
            for key, vectors in collected.items()
        }
        return BertRepresentations(
            vectors=stacked,
            wordpiece_counts=np.asarray(counts, dtype=np.int16).reshape(len(rows), 2),
            device=str(self.device),
            model=self.config.model,
            revision=self.config.revision,
        )
