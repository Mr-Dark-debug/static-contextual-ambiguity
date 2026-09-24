# Three Poster Variations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build three independently readable A1 poster PDFs from the approved standard, question-led, and concise structures without changing the canonical exam submission.

**Architecture:** A shared LaTeX style file owns the page geometry, typography, colors, title block, and reusable result callouts. Three focused TeX documents own their distinct information architecture. A Python build script compiles each source, copies stable outputs to `output/pdf/`, and a separate verifier checks format, content, identity, and result provenance.

**Tech Stack:** LaTeX with Tectonic, Python 3.11, `pypdf`, `pdfplumber`, Poppler `pdftoppm`, pytest, uv, Git, and GitHub CLI.

## Global Constraints

- Preserve `submission/poster.pdf` and `submission/appendix.pdf` unchanged.
- Preserve `submission/` as exactly those two canonical files.
- Create three one-page A1 portrait PDFs under `output/pdf/`.
- Use the official University Trier vector logo and the supplied author names and enrollment numbers.
- Reuse `poster/generated_results.tex` so displayed results remain traceable to committed artifacts.
- Use the verified citation names and years in `references/references.bib`.
- Integrate one short scope statement into each conclusion; do not create a limitations panel.
- Render and visually inspect every final PDF before delivery.

---

### Task 1: Add poster-variation verification tests

**Files:**
- Create: `tests/test_poster_variations.py`
- Create: `scripts/verify_poster_variations.py`

**Interfaces:**
- Consumes: PDFs in `output/pdf/`, values in `results/final/metrics.csv`, and author identity in `poster/authors.tex`.
- Produces: `verify_variations(root: Path) -> None`, which raises `RuntimeError` on any failed gate.

- [ ] **Step 1: Write failing tests for required files and result tracing**

```python
from pathlib import Path
from runpy import run_path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = run_path(str(ROOT / "scripts/verify_poster_variations.py"))
EXPECTED = {
    "poster_variation_1_standard.pdf",
    "poster_variation_2_questions.pdf",
    "poster_variation_3_concise.pdf",
}


def test_expected_variant_names_are_stable() -> None:
    assert VERIFY["EXPECTED_FILES"] == EXPECTED


def test_missing_output_directory_fails(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="missing poster variation directory"):
        VERIFY["verify_variations"](tmp_path)
```

- [ ] **Step 2: Run the tests and confirm the missing verifier fails**

Run: `uv run pytest tests/test_poster_variations.py -q`

Expected: FAIL because `scripts/verify_poster_variations.py` does not exist.

- [ ] **Step 3: Implement the verifier boundary and exact output set**

```python
from pathlib import Path

from pypdf import PdfReader

EXPECTED_FILES = {
    "poster_variation_1_standard.pdf",
    "poster_variation_2_questions.pdf",
    "poster_variation_3_concise.pdf",
}
A1_POINTS = (1683.78, 2383.94)


def verify_variations(root: Path) -> None:
    output = root / "output/pdf"
    if not output.is_dir():
        raise RuntimeError(f"missing poster variation directory: {output}")
    actual = {path.name for path in output.glob("*.pdf")}
    if actual != EXPECTED_FILES:
        raise RuntimeError(f"poster variation file gate failed: {sorted(actual)}")
    for name in sorted(EXPECTED_FILES):
        reader = PdfReader(output / name)
        if len(reader.pages) != 1:
            raise RuntimeError(f"{name} must contain exactly one page")
```

- [ ] **Step 4: Extend tests for A1 dimensions, required sections, authors, and result values**

Add small test PDFs or monkeypatched readers that prove the verifier rejects a wrong page count, a wrong media box, a missing author, a missing conceptual definition, and a changed reported accuracy. Keep the expected text list explicit per variation rather than using one generic heading set.

- [ ] **Step 5: Run focused tests**

Run: `uv run pytest tests/test_poster_variations.py -q`

Expected: PASS.

- [ ] **Step 6: Commit the verification boundary**

```powershell
git add scripts/verify_poster_variations.py tests/test_poster_variations.py
git commit -m "test poster variation release gates"
```

### Task 2: Create the shared visual system and standard poster

**Files:**
- Create: `poster/variations/shared_style.tex`
- Create: `poster/variations/poster_variation_1_standard.tex`
- Modify: `scripts/verify_poster_variations.py`

**Interfaces:**
- Consumes: `poster/authors.tex`, `poster/generated_results.tex`, `poster/assets/university-trier.pdf`, and `figures/poster_accuracy.pdf`.
- Produces: a standalone TeX source compiling to `poster_variation_1_standard.pdf`.

- [ ] **Step 1: Define shared A1 geometry, palette, title block, and result callouts**

The shared style must define `\bodyfont`, `\sectiontitle`, `\divider`, `\PosterHeader`, and `\ResultCallout`. It must resolve shared inputs relative to the repository root and use the current navy, Trier blue, orange, and rule gray colors.

```tex
\usepackage[paperwidth=594mm,paperheight=841mm,top=17mm,bottom=17mm,left=20mm,right=20mm]{geometry}
\newcommand{\bodyfont}{\fontsize{26}{32}\selectfont}
\newcommand{\ResultCallout}[2]{%
  \begin{minipage}[t]{0.31\linewidth}\centering
  {\fontsize{42}{48}\selectfont\bfseries\textcolor{blue}{#1}\par}
  {\fontsize{22}{27}\selectfont #2}
  \end{minipage}}
```

- [ ] **Step 2: Implement the three-column standard narrative**

Use the supplied Introduction, Background, Related Work, Hypotheses, Methodology, Results, Discussion, and Conclusion content. Replace raw numeric claims with generated macros such as `\TargetAccuracy`, `\ContextAccuracy`, `\BertAccuracy`, `\BertMacroF`, `\BertAuc`, `\AccuracyGain`, `\GainLower`, `\GainUpper`, `\BertOnlyCount`, `\StaticOnlyCount`, and `\BertErrorCount`.

- [ ] **Step 3: Compile the source manually**

Run from `poster/variations/`:

```powershell
tectonic -X compile --outdir . --outfmt pdf --print --untrusted poster_variation_1_standard.tex
```

Expected: one A1 PDF with no LaTeX error and no overfull box warning that affects visible content.

- [ ] **Step 4: Run the verifier and focused test**

Copy the compiled PDF temporarily to its stable output path, then run:

```powershell
uv run pytest tests/test_poster_variations.py -q
uv run python scripts/verify_poster_variations.py
```

Expected: the standard poster passes; absent variants are reported until Task 4 completes.

- [ ] **Step 5: Commit the shared system and standard source**

```powershell
git add poster/variations/shared_style.tex poster/variations/poster_variation_1_standard.tex scripts/verify_poster_variations.py
git commit -m "add standard academic poster variation"
```

### Task 3: Create question-led and concise poster sources

**Files:**
- Create: `poster/variations/poster_variation_2_questions.tex`
- Create: `poster/variations/poster_variation_3_concise.tex`
- Modify: `tests/test_poster_variations.py`

**Interfaces:**
- Consumes: the commands from `poster/variations/shared_style.tex` and the same generated data inputs as Task 2.
- Produces: two standalone TeX sources with distinct reading structures.

- [ ] **Step 1: Implement the question-led two-column source**

Use the eight approved question headings verbatim. Place a full-width result band between the upper conceptual questions and lower methodological/error-analysis questions. The result band must include the three accuracy values and the 11.6-point paired gain.

- [ ] **Step 2: Implement the concise eight-section source**

Use numbered headings 1 through 8, short bullets, and larger number callouts. Preserve definitions for ambiguity, homonymy, polysemy, embeddings, cosine similarity, and WiC even though this version is shorter.

- [ ] **Step 3: Add structural assertions for the two new sources**

```python
def test_question_source_uses_all_question_headings() -> None:
    source = (ROOT / "poster/variations/poster_variation_2_questions.tex").read_text()
    for heading in ("What is the problem?", "What did we do?", "Where do they fail?", "So what?"):
        assert heading in source


def test_concise_source_keeps_concept_definitions() -> None:
    source = (ROOT / "poster/variations/poster_variation_3_concise.tex").read_text()
    for term in ("Lexical ambiguity", "Homonymy", "Polysemy", "Cosine similarity", "WiC"):
        assert term in source
```

- [ ] **Step 4: Run focused tests and compile both sources**

Run:

```powershell
uv run pytest tests/test_poster_variations.py -q
tectonic -X compile --outdir poster/variations --outfmt pdf --print --untrusted poster/variations/poster_variation_2_questions.tex
tectonic -X compile --outdir poster/variations --outfmt pdf --print --untrusted poster/variations/poster_variation_3_concise.tex
```

Expected: tests pass and both PDFs compile as single A1 pages.

- [ ] **Step 5: Commit the two sources**

```powershell
git add poster/variations/poster_variation_2_questions.tex poster/variations/poster_variation_3_concise.tex tests/test_poster_variations.py
git commit -m "add question-led and concise poster variations"
```

### Task 4: Automate the build and create stable PDF outputs

**Files:**
- Create: `scripts/build_poster_variations.py`
- Create: `output/pdf/poster_variation_1_standard.pdf`
- Create: `output/pdf/poster_variation_2_questions.pdf`
- Create: `output/pdf/poster_variation_3_concise.pdf`
- Modify: `README.md`

**Interfaces:**
- Consumes: the three TeX sources and a resolved Tectonic executable path.
- Produces: `build_variations(root: Path, tectonic: Path) -> tuple[Path, ...]` returning the three stable PDF paths.

- [ ] **Step 1: Mark the PDF edit operation once**

Run from the installed PDF skill root:

```powershell
node container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 3 --output-format pdf
```

Expected: success before the first PDF-authoring command.

- [ ] **Step 2: Add a failing build-map test**

```python
def test_build_map_has_three_stable_outputs() -> None:
    build = run_path(str(ROOT / "scripts/build_poster_variations.py"))
    assert build["VARIATIONS"] == {
        "poster_variation_1_standard.tex": "poster_variation_1_standard.pdf",
        "poster_variation_2_questions.tex": "poster_variation_2_questions.pdf",
        "poster_variation_3_concise.tex": "poster_variation_3_concise.pdf",
    }
```

- [ ] **Step 3: Implement deterministic compilation and copying**

The script must run Tectonic once per source with `check=True`, create `output/pdf/`, copy only the expected PDFs, and remove stale unexpected PDFs from that output directory only after resolving and validating that the directory is exactly `<root>/output/pdf`.

- [ ] **Step 4: Document the comparison outputs**

Add a README section explaining that `submission/` remains the canonical two-file exam package and that the three comparison posters are built with:

```powershell
uv run python scripts/build_poster_variations.py --tectonic "C:\path\to\tectonic.exe"
uv run python scripts/verify_poster_variations.py
```

- [ ] **Step 5: Build and verify the three PDFs**

Run the build command with the detected Tectonic executable, then:

```powershell
uv run python scripts/verify_poster_variations.py
```

Expected: exactly three named PDFs, each one-page A1 portrait, with all content and provenance gates passing.

- [ ] **Step 6: Commit the build outputs**

```powershell
git add scripts/build_poster_variations.py scripts/verify_poster_variations.py README.md output/pdf/*.pdf poster/variations/*.pdf
git commit -m "build three A1 poster variations"
```

### Task 5: Visual QA, regression checks, and GitHub publication

**Files:**
- Create temporarily: `tmp/pdfs/poster_variation_*.png`
- Modify after visual inspection when a named defect is found: the specific affected file under `poster/variations/*.tex`
- Modify: `docs/superpowers/plans/2026-09-24-three-poster-variations.md`

**Interfaces:**
- Consumes: final PDFs from Task 4.
- Produces: visually approved PDFs and a pushed `main` branch whose remote SHA matches local HEAD.

- [ ] **Step 1: Render every poster at inspection resolution**

```powershell
pdftoppm -png -r 150 -singlefile output/pdf/poster_variation_1_standard.pdf tmp/pdfs/poster_variation_1_standard
pdftoppm -png -r 150 -singlefile output/pdf/poster_variation_2_questions.pdf tmp/pdfs/poster_variation_2_questions
pdftoppm -png -r 150 -singlefile output/pdf/poster_variation_3_concise.pdf tmp/pdfs/poster_variation_3_concise
```

- [ ] **Step 2: Inspect all three rendered pages**

Check title balance, author alignment, reading order, chart legibility, whitespace, section balance, reference readability, bottom margin, clipping, collisions, and stray glyphs. Revise and rebuild until all three have zero visible defects.

- [ ] **Step 3: Run complete validation**

```powershell
uv run pytest -q
uv run ruff check .
uv run python scripts/verify_poster_variations.py
uv run python scripts/verify_submission.py
git diff --check
```

Expected: all tests pass, Ruff passes, all three variation checks pass, canonical submission verification passes, and `git diff --check` returns no output.

- [ ] **Step 4: Record completion and commit final refinements**

Mark every plan checkbox complete. Commit any visual refinements, regenerated PDFs, and the completed plan:

```powershell
git add docs/superpowers/plans/2026-09-24-three-poster-variations.md poster/variations output/pdf scripts tests README.md
git commit -m "verify and publish poster variations"
```

- [ ] **Step 5: Push and verify the remote revision**

```powershell
git push origin main
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected: clean `main...origin/main` status and identical local and remote commit SHAs.
