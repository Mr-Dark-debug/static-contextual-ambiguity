# Poster readability redesign implementation plan

**Goal:** Rebuild the poster with a centered identity, open layout and simple charts.

**Architecture:** Add a focused poster chart module consuming frozen CSV artifacts.
Retain the earlier research figures. Rewrite the LaTeX page and adapt result
traceability checks to the figures and claims actually displayed.

**Tech stack:** Python 3.11, pandas, Matplotlib, LaTeX/Tectonic, Poppler, pypdf.

## Constraints

Follow the 2026-09-13 redesign specification. Preserve the empirical results and
appendix. Execute inline under the user's instruction to keep going. Both names
and enrollment numbers were supplied by the user and are stored in `poster/authors.tex`.

## Tasks

- [x] Add `visualization/poster_charts.py` with an accuracy dot/interval chart and
  paired-outcome bar chart. Read metrics, confidence intervals and predictions.
  Derive four disjoint categories directly from both correctness columns.
  Verify their counts sum to 638 and reconstruct each model's accuracy.
- [x] Extend `scripts/generate_figures.py` to generate the new poster figures.
  Add correctness checks for outcome partitioning, including neither-correct
  cases irrespective of the third diagnostic model.
- [x] Add the official logo vector, conversion instructions and source note.
- [x] Rewrite `poster/poster.tex`, center identity data in `poster/authors.tex`,
  and update `poster/Makefile` figure dependencies. Use short sentences.
- [x] Extend generated result macros with correct counts and the positive gain
  interval. Update submission verification to trace displayed values, require
  centered author metadata and the official logo, and reject removed panels.
- [x] Generate charts, compile the poster, render at 150 PPI, inspect and revise
  spacing and typography. Stage the poster without changing the appendix.
- [x] Run applicable tests, Ruff and submission verification. Update the narrative
  and checklist with the new presentation. Inspect the final diff and commit.

## Completed refinement

The user requested a stronger explanation after seeing the open design. The
poster now starts with definitions, explains both model mechanisms and related
sense-disambiguation methods, then presents hypothesis, methodology, accuracy
results and conclusion. The paired-outcome chart remains supplementary.

Verification: 59 tests passed, Ruff passed, one A1 page with six embedded fonts,
11 traced result values, user-supplied identity, no removed panels, exactly two
submission PDFs. The eight-page appendix and all empirical result files are unchanged.
