"""Acquire and validate the exact WiC release used by the experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import urllib.parse
import zipfile
from collections import Counter
from collections.abc import Iterable
from pathlib import Path, PurePosixPath
from typing import Any

import httpx

from lexical_ambiguity.types import DataAudit, WicExample

EXPECTED_SPLIT_FILES = {
    "train": "WiC/train.jsonl",
    "val": "WiC/val.jsonl",
    "test": "WiC/test.jsonl",
}
EXPECTED_RELEASE_COUNTS = {"train": 5428, "val": 638, "test": 1400}


class DataValidationError(ValueError):
    """Raised when downloaded or parsed data violate the frozen protocol."""


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f"{destination.name}.", suffix=".part", dir=destination.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        try:
            with httpx.stream("GET", url, follow_redirects=True, timeout=120.0) as response:
                response.raise_for_status()
                for chunk in response.iter_bytes():
                    temporary.write(chunk)
            temporary.flush()
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
    temporary_path.replace(destination)


def _is_unsafe_member(name: str) -> bool:
    path = PurePosixPath(name.replace("\\", "/"))
    return path.is_absolute() or ".." in path.parts


def _extract_release(archive: Path, processed_dir: Path) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(archive) as bundle:
            unsafe = [
                info.filename for info in bundle.infolist() if _is_unsafe_member(info.filename)
            ]
            if unsafe:
                raise DataValidationError(f"unsafe archive member: {unsafe[0]}")
            available = set(bundle.namelist())
            missing = set(EXPECTED_SPLIT_FILES.values()) - available
            if missing:
                raise DataValidationError(f"archive is missing WiC files: {sorted(missing)}")
            for split, member_name in EXPECTED_SPLIT_FILES.items():
                destination = processed_dir / f"{split}.jsonl"
                with (
                    bundle.open(member_name) as source,
                    tempfile.NamedTemporaryFile(
                        prefix=f"{split}.", suffix=".part", dir=processed_dir, delete=False
                    ) as temporary,
                ):
                    temporary_path = Path(temporary.name)
                    shutil.copyfileobj(source, temporary)
                temporary_path.replace(destination)
    except zipfile.BadZipFile as error:
        raise DataValidationError(f"invalid WiC ZIP archive: {archive}") from error


def ensure_wic_data(
    *,
    url: str,
    expected_sha256: str,
    raw_dir: Path,
    processed_dir: Path,
    archive_source: Path | None = None,
    force: bool = False,
) -> Path:
    """Download, checksum, and safely extract the frozen WiC archive.

    ``archive_source`` exists for offline verification and tests. It is never
    copied over a project archive, which keeps those checks side-effect-light.
    """

    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    archive = Path(archive_source) if archive_source is not None else raw_dir / "WiC.zip"
    if archive_source is None and (force or not archive.exists()):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"https", "http"}:
            raise DataValidationError("dataset URL must use HTTP(S)")
        _download(url, archive)
    if not archive.exists():
        raise DataValidationError(f"WiC archive does not exist: {archive}")

    actual_sha256 = sha256_file(archive)
    if actual_sha256.lower() != expected_sha256.lower():
        raise DataValidationError(
            f"dataset checksum mismatch: expected {expected_sha256}, got {actual_sha256}"
        )

    destinations = [processed_dir / f"{split}.jsonl" for split in EXPECTED_SPLIT_FILES]
    if force or not all(path.exists() for path in destinations):
        _extract_release(archive, processed_dir)
    return processed_dir


def _strict_int(raw: Any, name: str, idx: Any) -> int:
    if not isinstance(raw, int) or isinstance(raw, bool):
        raise DataValidationError(f"example {idx}: {name} must be an integer")
    return raw


def parse_example(raw: dict[str, Any], split: str) -> WicExample:
    required = {
        "word",
        "sentence1",
        "sentence2",
        "idx",
        "start1",
        "start2",
        "end1",
        "end2",
        "version",
    }
    missing = required - set(raw)
    if missing:
        raise DataValidationError(
            f"example {raw.get('idx', '?')}: missing fields {sorted(missing)}"
        )

    idx = _strict_int(raw["idx"], "idx", raw.get("idx", "?"))
    word = raw["word"]
    sentence1 = raw["sentence1"]
    sentence2 = raw["sentence2"]
    if not isinstance(word, str) or not word.strip():
        raise DataValidationError(f"example {idx}: word must be non-empty text")
    if not isinstance(sentence1, str) or not sentence1.strip():
        raise DataValidationError(f"example {idx}: sentence1 must be non-empty text")
    if not isinstance(sentence2, str) or not sentence2.strip():
        raise DataValidationError(f"example {idx}: sentence2 must be non-empty text")

    starts_ends = {
        name: _strict_int(raw[name], name, idx) for name in ("start1", "end1", "start2", "end2")
    }
    for side, sentence in ((1, sentence1), (2, sentence2)):
        start = starts_ends[f"start{side}"]
        end = starts_ends[f"end{side}"]
        if start < 0 or end <= start or end > len(sentence):
            raise DataValidationError(
                f"example {idx}: invalid target span {start}:{end} for sentence{side} "
                f"of length {len(sentence)}"
            )
        if not sentence[start:end].strip():
            raise DataValidationError(f"example {idx}: target span {side} is empty")

    label = raw.get("label")
    if label is None:
        if split != "test":
            raise DataValidationError(f"example {idx}: label is required for split {split}")
    elif not isinstance(label, bool):
        raise DataValidationError(f"example {idx}: label must be boolean")

    return WicExample(
        idx=idx,
        word=word,
        sentence1=sentence1,
        sentence2=sentence2,
        start1=starts_ends["start1"],
        end1=starts_ends["end1"],
        start2=starts_ends["start2"],
        end2=starts_ends["end2"],
        label=label,
        version=str(raw["version"]),
        split=split,
    )


def load_wic_split(processed_dir: Path, split: str) -> list[WicExample]:
    path = Path(processed_dir) / f"{split}.jsonl"
    examples: list[WicExample] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as error:
                    raise DataValidationError(
                        f"{path.name}:{line_number}: invalid JSON: {error.msg}"
                    ) from error
                if not isinstance(raw, dict):
                    raise DataValidationError(f"{path.name}:{line_number}: row must be an object")
                examples.append(parse_example(raw, split))
    except OSError as error:
        raise DataValidationError(f"could not read split file {path}: {error}") from error
    if not examples:
        raise DataValidationError(f"split {split} is empty")
    return examples


def _ordered_task_key(example: WicExample) -> tuple[object, ...]:
    return (
        example.word.casefold(),
        example.sentence1,
        example.start1,
        example.end1,
        example.sentence2,
        example.start2,
        example.end2,
    )


def _symmetric_task_key(example: WicExample) -> tuple[object, ...]:
    sides = sorted(
        (
            (example.sentence1, example.start1, example.end1),
            (example.sentence2, example.start2, example.end2),
        )
    )
    return (example.word.casefold(), *sides[0], *sides[1])


def audit_examples(examples: Iterable[WicExample], split: str) -> DataAudit:
    rows = list(examples)
    if not rows:
        raise DataValidationError(f"split {split} is empty")
    ids = Counter(item.idx for item in rows)
    duplicate_ids = sorted(idx for idx, count in ids.items() if count > 1)
    if duplicate_ids:
        raise DataValidationError(f"split {split} has duplicate IDs: {duplicate_ids[:5]}")
    ordered_tasks = Counter(_ordered_task_key(item) for item in rows)
    duplicate_tasks = sum(1 for count in ordered_tasks.values() if count > 1)
    if duplicate_tasks:
        raise DataValidationError(f"split {split} has duplicate task rows: {duplicate_tasks}")
    symmetric_tasks = Counter(_symmetric_task_key(item) for item in rows)
    symmetric_duplicates = sum(count - 1 for count in symmetric_tasks.values() if count > 1)

    labels = [item.label for item in rows]
    positive = sum(label is True for label in labels)
    negative = sum(label is False for label in labels)
    mismatches = 0
    repeated = 0
    contains_space = 0
    empty_spans = 0
    maximum_length = 0
    for item in rows:
        surfaces = (item.target_surface(1), item.target_surface(2))
        if any(surface.casefold() != item.word.casefold() for surface in surfaces):
            mismatches += 1
        if any(" " in surface for surface in surfaces):
            contains_space += 1
        if any(not surface.strip() for surface in surfaces):
            empty_spans += 1
        if (
            item.sentence1.casefold().count(surfaces[0].casefold()) > 1
            or item.sentence2.casefold().count(surfaces[1].casefold()) > 1
        ):
            repeated += 1
        maximum_length = max(maximum_length, len(item.sentence1), len(item.sentence2))

    return DataAudit(
        split=split,
        examples=len(rows),
        labeled=positive + negative,
        positive=positive,
        negative=negative,
        unlabeled=sum(label is None for label in labels),
        unique_words=len({item.word.casefold() for item in rows}),
        surface_lemma_mismatch=mismatches,
        repeated_surface_contexts=repeated,
        symmetric_duplicate_pairs=symmetric_duplicates,
        surface_contains_space=contains_space,
        empty_spans=empty_spans,
        max_sentence_characters=maximum_length,
    )


def validate_no_cross_split_pairs(
    first: Iterable[WicExample], second: Iterable[WicExample]
) -> None:
    overlap = {_symmetric_task_key(item) for item in first} & {
        _symmetric_task_key(item) for item in second
    }
    if overlap:
        raise DataValidationError(f"found {len(overlap)} cross-split duplicate sentence pairs")


def validate_expected_release(audits: Iterable[DataAudit]) -> None:
    by_split = {audit.split: audit for audit in audits}
    for split, expected_count in EXPECTED_RELEASE_COUNTS.items():
        if split not in by_split:
            raise DataValidationError(f"missing audit for split {split}")
        audit = by_split[split]
        if audit.examples != expected_count:
            raise DataValidationError(
                f"split {split} has {audit.examples} examples; expected {expected_count}"
            )
    for split in ("train", "val"):
        audit = by_split[split]
        if audit.unlabeled or audit.positive != audit.negative:
            raise DataValidationError(f"split {split} is not fully labeled and balanced")
    if by_split["test"].labeled:
        raise DataValidationError("SuperGLUE v2 test unexpectedly contains labels")
