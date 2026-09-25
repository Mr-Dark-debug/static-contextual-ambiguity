"""Verify the two active A1 comparison posters and their evidence traceability."""

from __future__ import annotations

import csv
import unicodedata
from collections.abc import Iterator
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import DictionaryObject

EXPECTED_FILES = {
    "poster_variation_1_standard.pdf",
    "poster_variation_2_questions.pdf",
}
A1_POINTS = (1683.78, 2383.94)
COMMON_TEXT = (
    "Choudhary Prashant Santosh",
    "1910474",
    "Rahul Khunt",
    "1911272",
    "University of Trier",
    "Lexical ambiguity",
    "Homonymy",
    "Polysemy",
    "GloVe",
    "BERT",
    "WiC",
    "Methodology",
    "Results",
    "Conclusion",
    "Pilehvar",
    "Camacho-Collados",
    "Pennington",
    "Devlin",
)
VARIANT_TEXT = {
    "poster_variation_1_standard.pdf": (
        "Introduction",
        "Background",
        "Hypotheses",
        "Discussion",
    ),
    "poster_variation_2_questions.pdf": (
        "What is the problem?",
        "Hypothesis",
        "What did we do?",
        "What did we find?",
        "Where do they fail?",
        "So what?",
    ),
}


def _normal_text(reader: PdfReader) -> str:
    text = " ".join(" ".join(page.extract_text() or "" for page in reader.pages).split())
    text = unicodedata.normalize("NFKC", text)
    return text.replace("T rier", "Trier").replace("T rends", "Trends")


def _walk_fonts(resources: DictionaryObject) -> Iterator[DictionaryObject]:
    fonts = resources.get("/Font")
    if fonts:
        for reference in fonts.get_object().values():
            yield reference.get_object()
    xobjects = resources.get("/XObject")
    if xobjects:
        for reference in xobjects.get_object().values():
            xobject = reference.get_object()
            nested = xobject.get("/Resources")
            if nested:
                yield from _walk_fonts(nested.get_object())


def _font_is_embedded(font: DictionaryObject) -> bool:
    if font.get("/Subtype") == "/Type3" and font.get("/CharProcs"):
        return True
    candidates = [font]
    descendants = font.get("/DescendantFonts")
    if descendants:
        candidates.extend(ref.get_object() for ref in descendants.get_object())
    for candidate in candidates:
        descriptor = candidate.get("/FontDescriptor")
        if descriptor:
            descriptor = descriptor.get_object()
            if any(descriptor.get(key) for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                return True
    return False


def _verify_fonts(reader: PdfReader, name: str) -> int:
    fonts: dict[str, bool] = {}
    for page in reader.pages:
        resources = page.get("/Resources")
        if resources:
            for font in _walk_fonts(resources.get_object()):
                font_name = str(font.get("/BaseFont", "unnamed"))
                fonts[font_name] = fonts.get(font_name, False) or _font_is_embedded(font)
    missing = sorted(font for font, embedded in fonts.items() if not embedded)
    if not fonts or missing:
        raise RuntimeError(f"{name} has missing or non-embedded fonts: {missing}")
    return len(fonts)


def _required_result_fragments(root: Path) -> tuple[str, ...]:
    with (root / "results/final/metrics.csv").open(encoding="utf-8", newline="") as handle:
        metrics = {row["system"]: row for row in csv.DictReader(handle)}
    with (root / "results/final/paired_differences.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        paired = list(csv.DictReader(handle))
    difference = next(
        row
        for row in paired
        if row["contrast"] == "glove_context_2 - bert_mean_last_four"
        and row["metric"] == "accuracy"
    )
    target = metrics["glove_target"]
    context = metrics["glove_context_2"]
    bert = metrics["bert_mean_last_four"]
    return (
        f"{float(target['accuracy']) * 100:.1f}%",
        f"{float(context['accuracy']) * 100:.1f}%",
        f"{float(bert['accuracy']) * 100:.1f}%",
        f"{(float(bert['accuracy']) - float(context['accuracy'])) * 100:.1f}",
        f"{-float(difference['upper']) * 100:.1f}",
        f"{-float(difference['lower']) * 100:.1f}",
        "178",
        "104",
        "210",
        "638",
    )


def _verify_sources(root: Path) -> None:
    source_dir = root / "poster/variations"
    for source_name in (
        "poster_variation_1_standard.tex",
        "poster_variation_2_questions.tex",
    ):
        source = (source_dir / source_name).read_text(encoding="utf-8")
        for marker in (
            r"\input{shared_style.tex}",
            r"\TargetAccuracy",
            r"\ContextAccuracy",
            r"\BertAccuracy",
            r"\AccuracyGain",
            r"\GainLower",
            r"\GainUpper",
        ):
            if marker not in source:
                raise RuntimeError(f"{source_name} is missing generated marker {marker}")
    style = (source_dir / "shared_style.tex").read_text(encoding="utf-8")
    for marker in (
        r"paperwidth=594mm,paperheight=841mm",
        r"\input{../generated_results.tex}",
        r"\input{../authors.tex}",
        r"../../assets/university-trier.pdf",
        r"\newcommand{\bodyfont}{\fontsize{25}{31}\selectfont}",
    ):
        if marker not in style:
            raise RuntimeError(f"shared poster style is missing {marker}")


def verify_variations(root: Path) -> None:
    root = root.resolve()
    output = root / "output/pdf"
    if not output.is_dir():
        raise RuntimeError(f"missing poster variation directory: {output}")
    actual = {path.name for path in output.glob("*.pdf")}
    if actual != EXPECTED_FILES:
        raise RuntimeError(f"poster variation file gate failed: {sorted(actual)}")
    _verify_sources(root)
    result_fragments = _required_result_fragments(root)
    reports: list[str] = []
    for name in sorted(EXPECTED_FILES):
        reader = PdfReader(output / name)
        if len(reader.pages) != 1:
            raise RuntimeError(f"{name} must contain exactly one page")
        page = reader.pages[0]
        actual_size = (float(page.mediabox.width), float(page.mediabox.height))
        wrong_size = any(
            abs(value - expected) > 0.1
            for value, expected in zip(actual_size, A1_POINTS, strict=True)
        )
        if wrong_size:
            raise RuntimeError(f"{name} has page size {actual_size}, expected {A1_POINTS}")
        text = _normal_text(reader)
        required = COMMON_TEXT + VARIANT_TEXT[name] + result_fragments
        folded_text = text.casefold()
        missing = [fragment for fragment in required if fragment.casefold() not in folded_text]
        if missing:
            raise RuntimeError(f"{name} is missing required text: {missing}")
        if "??" in text:
            raise RuntimeError(f"{name} contains an unresolved LaTeX reference")
        font_count = _verify_fonts(reader, name)
        reports.append(f"{name}: {len(text)} characters, {font_count} embedded fonts")
    print("Poster variations verified: one A1 page each; " + "; ".join(reports))


def main() -> None:
    verify_variations(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
