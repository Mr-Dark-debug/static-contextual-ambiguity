import csv
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
RENDER = run_path(str(ROOT / "scripts/render_poster_copy.py"))["render"]
SOURCE = ROOT / "docs/poster_variation_1_text_draft.md"
GENERATED = ROOT / "poster/approved_copy.tex"


def test_all_approved_sections_and_closing_line_are_rendered() -> None:
    rendered = RENDER(SOURCE.read_text(encoding="utf-8"))
    for heading in (
        "Introduction",
        "Inspiration",
        "Background",
        "Hypothesis",
        "Methodology",
        "Results",
        "Conclusion",
    ):
        assert rf"\PosterSection{{{heading}}}" in rendered
    assert r"\PosterAccuracyChart" in rendered
    assert "even this human can seem difficult to disambiguate" in rendered
    assert rendered == GENERATED.read_text(encoding="utf-8")


def test_inline_formatting_preserves_the_approved_wording() -> None:
    rendered = RENDER("# Title\n\n## Introduction\n\n**Same** *bank* costs 50%.")
    assert r"\textbf{Same} \emph{bank} costs 50\%.\par" in rendered


def test_chart_widths_are_generated_from_saved_metrics() -> None:
    with (ROOT / "results/final/metrics.csv").open(encoding="utf-8", newline="") as handle:
        metrics = {row["system"]: row for row in csv.DictReader(handle)}
    macros = (ROOT / "poster/generated_results.tex").read_text(encoding="utf-8")
    source = (ROOT / "poster/poster.tex").read_text(encoding="utf-8")
    for system, name in (
        ("glove_target", "TargetAccuracyFraction"),
        ("glove_context_2", "ContextAccuracyFraction"),
        ("bert_mean_last_four", "BertAccuracyFraction"),
    ):
        expected = float(metrics[system]["accuracy"])
        assert rf"\newcommand{{\{name}}}{{{expected:.6f}}}" in macros
        assert rf"\{name}" in source
