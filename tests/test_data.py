import json
import zipfile
from pathlib import Path

import pytest

from lexical_ambiguity.data import (
    DataValidationError,
    audit_examples,
    ensure_wic_data,
    load_wic_split,
    parse_example,
    validate_no_cross_split_pairs,
)


def row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "word": "bank",
        "sentence1": "The bank approved the loan.",
        "sentence2": "We rested on the bank of the river.",
        "idx": 7,
        "label": False,
        "start1": 4,
        "start2": 17,
        "end1": 8,
        "end2": 21,
        "version": 1.1,
    }
    base.update(overrides)
    return base


def test_parse_example_preserves_half_open_target_spans() -> None:
    example = parse_example(row(), "train")

    assert example.label is False
    assert example.target_surface(1) == "bank"
    assert example.target_surface(2) == "bank"


def test_inflected_surface_is_valid_for_lemma() -> None:
    example = parse_example(
        row(
            word="summer",
            sentence1="We summered in Kashmir.",
            start1=3,
            end1=11,
        ),
        "train",
    )

    assert example.target_surface(1) == "summered"


def test_repeated_surface_uses_supplied_offset() -> None:
    sentence = "The bank sold the old bank building."
    second_start = sentence.rindex("bank")
    example = parse_example(
        row(sentence1=sentence, start1=second_start, end1=second_start + 4),
        "train",
    )

    assert example.start1 == second_start
    assert example.target_surface(1) == "bank"


def test_unlabeled_test_is_allowed_but_unlabeled_train_is_not() -> None:
    unlabeled = row()
    unlabeled.pop("label")

    assert parse_example(unlabeled, "test").label is None
    with pytest.raises(DataValidationError, match="label"):
        parse_example(unlabeled, "train")


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"start1": 9, "end1": 4}, "span"),
        ({"end2": 999}, "span"),
        ({"start1": 4, "end1": 4}, "span"),
        ({"label": "true"}, "boolean"),
    ],
)
def test_invalid_examples_fail_loudly(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(DataValidationError, match=message):
        parse_example(row(**overrides), "train")


def test_load_and_audit_balanced_jsonl(tmp_path: Path) -> None:
    rows = [
        row(idx=0, label=False),
        row(
            idx=1,
            label=True,
            sentence1="The bank collapsed.",
            sentence2="The bank opens early.",
            start2=4,
            end2=8,
        ),
    ]
    path = tmp_path / "train.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in rows) + "\n", encoding="utf-8")

    examples = load_wic_split(tmp_path, "train")
    audit = audit_examples(examples, "train")

    assert len(examples) == 2
    assert audit.positive == 1
    assert audit.negative == 1
    assert audit.empty_spans == 0


def test_audit_rejects_duplicate_ids_and_sentence_pairs() -> None:
    first = parse_example(row(idx=3), "train")
    duplicate = parse_example(row(idx=3), "train")

    with pytest.raises(DataValidationError, match="duplicate IDs"):
        audit_examples([first, duplicate], "train")

    second = parse_example(row(idx=4), "train")
    with pytest.raises(DataValidationError, match="duplicate task rows"):
        audit_examples([first, second], "train")


def test_cross_split_duplicate_pair_is_rejected() -> None:
    train = [parse_example(row(idx=1), "train")]
    validation = [parse_example(row(idx=2), "validation")]

    with pytest.raises(DataValidationError, match="cross-split"):
        validate_no_cross_split_pairs(train, validation)


def test_reversed_training_pair_is_reported_not_removed() -> None:
    first = parse_example(row(idx=1), "train")
    reversed_row = row(
        idx=2,
        sentence1=first.sentence2,
        start1=first.start2,
        end1=first.end2,
        sentence2=first.sentence1,
        start2=first.start1,
        end2=first.end1,
    )
    second = parse_example(reversed_row, "train")

    audit = audit_examples([first, second], "train")

    assert audit.examples == 2
    assert audit.symmetric_duplicate_pairs == 1


def test_ensure_wic_data_rejects_checksum_mismatch(tmp_path: Path) -> None:
    archive = tmp_path / "bad.zip"
    archive.write_bytes(b"not a zip")

    with pytest.raises(DataValidationError, match="checksum"):
        ensure_wic_data(
            url=archive.as_uri(),
            expected_sha256="0" * 64,
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "processed",
            archive_source=archive,
        )


def test_ensure_wic_data_rejects_unsafe_zip_member(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../escape.jsonl", "{}\n")
    import hashlib

    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    with pytest.raises(DataValidationError, match="unsafe archive member"):
        ensure_wic_data(
            url=archive.as_uri(),
            expected_sha256=checksum,
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "processed",
            archive_source=archive,
        )
