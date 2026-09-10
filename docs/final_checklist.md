# Final reproducibility and submission checklist

This checklist distinguishes completed project gates from the personal metadata that the
student must supply. Evidence was refreshed on 10 September 2026.

## Experiment and evidence

- [x] Python is constrained to 3.11 and all direct/transitive dependencies are frozen in
  `uv.lock`.
- [x] The official SuperGLUE v2 WiC archive checksum, expected members, split sizes,
  labels, and every half-open character span validate.
- [x] Target alignment selects every non-special WordPiece whose tokenizer offset overlaps
  the supplied target span; failures raise an error instead of guessing.
- [x] Model/window choice and all classification thresholds use official training data
  only. The selected configurations and integrity hash are saved in
  `results/raw/selection_ledger.json`.
- [x] The full 5,428-train / 638-validation experiment completed with the frozen GloVe and
  BERT revisions. The unlabeled 1,400-row test split has no reported score.
- [x] Accuracy, macro F1, positive-class precision/recall, ROC-AUC, confusion counts,
  paired 1,000-resample bootstrap intervals, layers 1--12, and row-level predictions are
  committed.
- [x] Qualitative examples come from saved prediction rows; interpretations are explicitly
  descriptive rather than causal.
- [x] A clean locked cached reproduction regenerated the full artifacts.

## Code and artifact gates

- [x] `uv sync --frozen --all-groups`
- [x] `uv run pytest -q` (57 tests)
- [x] `uv run ruff check .`
- [x] `uv run python scripts/run_quick_test.py`
- [x] `uv run python scripts/run_experiment.py` (full cache-integrity reproduction)
- [x] `uv run python scripts/analyse_results.py`
- [x] `uv run python scripts/generate_figures.py`
- [x] `uv run python scripts/build_submission.py --compile --stage --tectonic PATH`
- [x] `uv run python scripts/verify_submission.py`

The last verifier confirmed one 1683.78 x 2383.94 point A1 poster page, eight 595.28 x
841.89 point A4 appendix pages (one displayed in landscape), extractable required text,
embedded fonts, four 300-PPI figure previews, byte-identical staged copies, and exactly
`poster.pdf` plus `appendix.pdf` in `submission/`. The captured LaTeX build contains no
overfull-box or unresolved-reference warning.

## Human PDF review

- [x] Poster reviewed as a full-page raster: hierarchy, three-column reading order,
  body-text size, charts, labels, margins, and footer are readable with no clipping.
- [x] All eight appendix pages reviewed as rasters: tables, long URLs/hashes, rotated
  results table, references, page numbers, and declaration page render without clipping.
- [x] Poster visibly contains **Hypothesis**, **Methodology**, and **Results**.
- [x] Poster background/model claims use compact author-year citations; complete verified
  references and DOI links are in the appendix.
- [x] Results use “validation” consistently and do not disguise it as a public test score.

## Required personal action before hand-in

- [ ] Replace `Student Name`, student-ID, and repository-URL placeholders.
- [ ] Insert the exact institution-approved integrity declaration.
- [ ] Sign and date the declaration personally.
- [ ] Rebuild with `--declaration`, then rerun `scripts/verify_submission.py --signed`.

The present unsigned page is intentionally labeled as a placeholder. It is evidence that
the declaration slot exists, not a signature or claim of compliance.
