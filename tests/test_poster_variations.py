from pathlib import Path
from runpy import run_path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = run_path(str(ROOT / "scripts/verify_poster_variations.py"))
BUILD = run_path(str(ROOT / "scripts/build_poster_variations.py"))
EXPECTED = {
    "poster_variation_1_standard.pdf",
    "poster_variation_2_questions.pdf",
    "poster_variation_3_concise.pdf",
}


def test_expected_variant_names_are_stable() -> None:
    assert VERIFY["EXPECTED_FILES"] == EXPECTED
    assert set(BUILD["VARIATIONS"].values()) == EXPECTED


def test_missing_output_directory_fails(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="missing poster variation directory"):
        VERIFY["verify_variations"](tmp_path)


def test_question_source_uses_all_question_headings() -> None:
    source = (ROOT / "poster/variations/poster_variation_2_questions.tex").read_text()
    for heading in (
        "What is the problem?",
        "What did we do?",
        "What did we find?",
        "Where do they fail?",
        "So what?",
    ):
        assert heading in source


def test_concise_source_keeps_concept_definitions() -> None:
    source = (ROOT / "poster/variations/poster_variation_3_concise.tex").read_text()
    for term in ("Lexical ambiguity", "Homonymy", "Polysemy", "Cosine similarity", "WiC"):
        assert term in source


def test_each_source_uses_generated_results() -> None:
    for source in (ROOT / "poster/variations").glob("poster_variation_*.tex"):
        text = source.read_text()
        for macro in (
            r"\TargetAccuracy",
            r"\ContextAccuracy",
            r"\BertAccuracy",
            r"\AccuracyGain",
            r"\GainLower",
            r"\GainUpper",
        ):
            assert macro in text

