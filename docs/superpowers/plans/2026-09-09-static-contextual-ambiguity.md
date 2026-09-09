# Static vs Contextual Ambiguity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. In this workspace those sub-skills are unavailable, so the primary agent executes the same gates inline.

**Goal:** Run a reproducible WiC experiment comparing static target, static context, and pretrained BERT target representations, then build evidence-driven A1 poster and appendix PDFs.

**Architecture:** A typed Python package owns data validation, embedding extraction, thresholding, metrics, bootstrapping, analysis, and figures. Thin scripts load YAML configuration and call package services. Generated data, model caches, raw predictions, derived tables, figures, and final PDFs remain separated so every poster number can be traced to a saved artifact.

**Tech Stack:** Python 3.11 via uv, PyTorch, Transformers, NumPy, pandas, SciPy, scikit-learn, Matplotlib, PyYAML, pytest, Ruff, LaTeX/beamerposter, Poppler.

## Global Constraints

- Use the official SuperGLUE v2 WiC archive, SHA-256 `ee7e67f4ae9eafbf533780faa198e62167f3cda54256cdf261877be3c0e90900`.
- Tune windows, BERT pooling/layer choice, and decision thresholds on the 5,428 labeled training examples only.
- Treat the 638 labeled validation examples as final evaluation and never use its labels for selection.
- Do not report the 1,400-example SuperGLUE test split because its labels are absent.
- Compare GloVe 6B 300d static target, GloVe context averages, and unfine-tuned `google-bert/bert-base-uncased` target vectors.
- Align BERT subwords by half-open character-span overlap with tokenizer offset mappings.
- Report accuracy, macro F1, positive-class precision/recall, ROC-AUC, confusion matrices, and fixed-seed 95% bootstrap intervals.
- Produce only empirical, traceable numbers; do not cherry-pick after validation is opened.
- Final poster is one A1 portrait page, visibly containing Hypothesis, Methodology, and Results, with paragraph text at least 24 pt.
- `submission/` contains exactly `poster.pdf` and `appendix.pdf`; the integrity declaration remains unsigned unless the student supplies a signed file.

---

## File map

- `pyproject.toml`, `uv.lock`: runtime, dependency, lint, and test contract.
- `configs/*.yaml`: frozen quick and full experiment settings.
- `src/lexical_ambiguity/config.py`: validated configuration dataclasses and loader.
- `src/lexical_ambiguity/data.py`: official archive download, extraction, parsing, validation, and audit.
- `src/lexical_ambiguity/types.py`: immutable sample and result records.
- `src/lexical_ambiguity/embeddings/`: static-vector and BERT target encoders.
- `src/lexical_ambiguity/evaluation/`: similarity, train-only selection, metrics, bootstrap, paired comparisons, and error partitions.
- `src/lexical_ambiguity/experiment.py`: reproducible orchestration and artifact writing.
- `src/lexical_ambiguity/visualization/`: plots generated strictly from saved CSV/JSON results.
- `scripts/`: small command-line entry points.
- `tests/`: unit, regression, cache, and quick-pipeline tests.
- `docs/`: literature, design, decisions, writing guide, and evidence interpretation.
- `results/`, `figures/`: raw and derived empirical artifacts.
- `poster/`, `appendix/`, `submission/`: TeX sources, rendered artifacts, and final hand-in files.

### Task 1: Research protocol and bibliography

**Files:**
- Create: `docs/experiment_design.md`
- Create: `docs/literature_matrix.md`
- Create: `docs/writing_style_guide.md`
- Create: `docs/decisions.md`
- Create: `references/references.bib`

**Interfaces:**
- Consumes: ACL Anthology, original WiC site/archive, GloVe/BERT sources, poster-writing research.
- Produces: frozen claims, split protocol, citation keys, and design rules used by all later tasks.

- [ ] Record exact dataset counts, label availability, offset semantics, SHA-256, and non-commercial license.
- [ ] Record for each paper its question, data, model, experiment, finding, limitation, and only the claim it can support here.
- [ ] Correct supplied metadata: Loureiro et al. is the 2021 *Computational Linguistics* article; Haber and Poesio's title is *Patterns of Polysemy and Homonymy...*; Fodor et al. is an IWCS 2023 paper; Soper and Koenig is July 2022.
- [ ] Define the train-only selection ledger and the one-time validation evaluation rule.
- [ ] Run `git diff --check` and commit with `document research protocol`.

### Task 2: Project runtime and configuration

**Files:**
- Create: `pyproject.toml`, `.python-version`, `.gitignore`, `.env.example`, `README.md`
- Create: `configs/default.yaml`, `configs/quick_test.yaml`
- Create: package directories and `__init__.py` files.

**Interfaces:**
- Produces: `load_config(path: Path) -> ExperimentConfig` and an isolated Python 3.11 environment.

- [ ] Add a configuration test asserting seeds, split names, context candidates, BERT model, batch size, and output roots.
- [ ] Run the test and confirm it fails before `config.py` exists.
- [ ] Implement frozen dataclasses for data, GloVe, BERT, evaluation, and output options, rejecting unknown or invalid values.
- [ ] Run `uv sync --all-groups`, `uv run pytest tests/test_config.py -q`, and `uv run ruff check .`.
- [ ] Commit with `setup reproducible project`.

### Task 3: WiC acquisition and validation

**Files:**
- Create: `src/lexical_ambiguity/types.py`, `src/lexical_ambiguity/data.py`
- Create: `scripts/download_data.py`
- Create: `tests/test_data.py`
- Create: `data/README.md` and empty-directory sentinels.

**Interfaces:**
- Produces: `WicExample`, `download_wic(config) -> Path`, `load_wic_split(path, split) -> list[WicExample]`, and `audit_examples(examples) -> DataAudit`.

- [ ] Test boolean label parsing, missing test labels, half-open spans, inflected surface forms, repeated target surfaces, empty spans, duplicate IDs/pairs, and invalid offsets.
- [ ] Implement checksum-verified atomic download and safe ZIP extraction.
- [ ] Validate that each span selects a non-empty surface and each train/validation split is balanced with unique IDs.
- [ ] Download and audit all splits; save `data/processed/dataset_audit.json`.
- [ ] Run focused tests, Ruff, and commit with `validate wic data`.

### Task 4: Static GloVe representations

**Files:**
- Create: `src/lexical_ambiguity/embeddings/base.py`, `glove.py`
- Create: `tests/test_glove.py`

**Interfaces:**
- Produces: `EmbeddingStore.lookup(token)`, `StaticTargetEncoder.encode(example, side)`, `StaticContextEncoder.encode(example, side, window)`.

- [ ] Test case-normalized lookup, missing words, punctuation tokenization, exclusion of the exact target span, finite averages, and all-OOV handling.
- [ ] Implement a streaming loader for `glove.6B.300d.txt` with cached vocabulary vectors needed by WiC.
- [ ] Make Static Target use the lemma vector on both sides; log/exclude examples whose lemma is OOV.
- [ ] Build context tokens with regex character spans so repeated surface forms cannot remove the wrong occurrence.
- [ ] Run focused tests and commit with `add glove baselines`.

### Task 5: Similarity, selection, metrics, and bootstrap

**Files:**
- Create: `src/lexical_ambiguity/evaluation/similarity.py`, `threshold.py`, `metrics.py`, `bootstrap.py`
- Create: `tests/test_similarity.py`, `test_threshold.py`, `test_metrics.py`, `test_bootstrap.py`

**Interfaces:**
- Produces: `cosine_similarity(a, b)`, `select_threshold(scores, labels)`, `evaluate(scores, labels, threshold)`, `bootstrap_metrics(...)`.

- [ ] Test zero-vector rejection, similarity bounds, deterministic tie-breaking, positive-label direction, constant-score ROC-AUC, confusion layout, and fixed-seed CI reproducibility.
- [ ] Select thresholds from sorted score midpoints plus boundary candidates, maximizing macro F1 and breaking ties by accuracy then closeness to 0.5.
- [ ] Bootstrap paired example indices for 1,000 resamples and store percentile 95% intervals.
- [ ] Run focused tests and commit with `add evaluation metrics`.

### Task 6: BERT span alignment and encoder

**Files:**
- Create: `src/lexical_ambiguity/embeddings/bert.py`
- Create: `tests/test_bert_alignment.py`

**Interfaces:**
- Produces: `overlapping_token_indices(offsets, start, end)`, `pool_subwords(hidden, indices)`, and `BertTargetEncoder.encode_batch(...)`.

- [ ] Test exact, punctuation-adjacent, repeated, contracted, unusual-whitespace, and multi-WordPiece targets using fast-tokenizer offsets.
- [ ] Select tokens satisfying `token_end > target_start and token_start < target_end`, ignoring `(0, 0)` special-token offsets.
- [ ] Mean-pool WordPieces and emit each layer 1–12 plus mean-last-four in one inference pass under `model.eval()` and `torch.inference_mode()`.
- [ ] Use adaptive CUDA batch sizing with CPU fallback and actionable failure logs; never guess a token on alignment failure.
- [ ] Run focused/model tests and commit with `add bert target embeddings`.

### Task 7: Cache and quick pipeline

**Files:**
- Create: `src/lexical_ambiguity/utils.py`, `experiment.py`
- Create: `scripts/run_quick_test.py`, `scripts/run_experiment.py`
- Create: `tests/test_cache.py`, `tests/test_smoke.py`

**Interfaces:**
- Produces: cache keys containing data checksum, model revision, pooling, split, seed, and code schema; `run_experiment(config) -> ExperimentArtifacts`.

- [ ] Test cache round-trips, invalidation, atomic writes, deterministic quick sampling, and an injected tiny-encoder smoke run.
- [ ] Log Python, Torch, Transformers, CUDA, GPU, seed, resolved config, git commit, and dirty state.
- [ ] Ensure expensive BERT outputs are cached before scoring layers.
- [ ] Run the 50–100-pair quick configuration, inspect saved scores, and commit with `run quick pipeline`.

### Task 8: Freeze selections and run full experiment

**Files:**
- Create/update: `results/raw/*`, `results/final/config.json`, `docs/decisions.md`

**Interfaces:**
- Consumes: all training representations.
- Produces: frozen context window, primary BERT pooling/layer, and thresholds before validation is evaluated.

- [ ] Run all static context candidates and BERT candidates on train.
- [ ] Write a machine-readable selection ledger with candidate metrics and deterministic winners.
- [ ] Freeze configuration, then evaluate validation once for all three primary systems and all 12 BERT layers.
- [ ] Save `metrics.csv`, `bootstrap_ci.csv`, `predictions.csv`, confusion matrices, `layer_metrics.csv`, and environment metadata.
- [ ] Run sanity assertions and commit with `run full experiment`.

### Task 9: Statistical and error analysis

**Files:**
- Create: `src/lexical_ambiguity/evaluation/analysis.py`, `scripts/analyse_results.py`
- Create: `tests/test_analysis.py`
- Create: `results/examples/error_cases.csv`, `docs/results_interpretation.md`

**Interfaces:**
- Produces paired bootstrap differences and disjoint qualitative partitions.

- [ ] Test partitions for BERT-only correct, static-only correct, all-wrong, high-confidence error, and borderline cases.
- [ ] Compute paired bootstrap metric differences without claiming significance unless the 95% interval excludes zero.
- [ ] Inspect actual examples and report only visible recurring patterns, separating observations from explanations.
- [ ] State what the experiment can and cannot conclude; commit with `analyse experiment errors`.

### Task 10: Figures

**Files:**
- Create: `src/lexical_ambiguity/visualization/*.py`, `scripts/generate_figures.py`
- Create: `tests/test_figures.py`
- Generate: `figures/*.pdf`, `figures/*.svg`, `figures/*.png`

**Interfaces:**
- Consumes only frozen saved tables/predictions.
- Produces model comparison, similarity distributions, layer analysis, and a compact qualitative example.

- [ ] Test that plotted values equal source-table values and output PNG density is at least 150 PPI at placed size.
- [ ] Use color-blind-safe static-context/BERT colors; visually de-emphasize the diagnostic static-target bar.
- [ ] Keep titles declarative and evidence-bounded; commit with `plot final results`.

### Task 11: Evidence-led poster narrative and design

**Files:**
- Create: `docs/poster_narrative.md`, `poster/poster.tex`, `poster/Makefile`, `poster/assets/*`

**Interfaces:**
- Consumes: `docs/results_interpretation.md` and final figures.
- Produces: one A1 portrait poster with the mandatory three sections.

- [ ] Use the brainstorming skill now that empirical findings are known; choose the one strongest answer, one explanatory plot, and one nuance/failure.
- [ ] Draft compact observation → evidence → interpretation copy, with no unverified claims or placeholder results.
- [ ] Use off-white background, dark type, one controlled accent, three-column flow, and at least 24 pt body text.
- [ ] Add author/repository placeholders only where personal data or a real URL has not been supplied; label them plainly.
- [ ] Build and commit with `draft evidence led poster`.

### Task 12: Appendix and TeX build

**Files:**
- Create: `appendix/appendix.tex`, `appendix/integrity_declaration_PLACEHOLDER.pdf`
- Create: `scripts/build_submission.py`

**Interfaces:**
- Produces complete verified references and an unsigned declaration placeholder; appends a real signed PDF only when supplied.

- [ ] Detect/install a reproducible TeX engine following the LaTeX skill; record exact tooling.
- [ ] Build poster and appendix from a clean state and fail on unresolved references, missing citations, or overfull content.
- [ ] Never generate or imitate a signature; commit with `build appendix`.

### Task 13: Rendered-PDF inspection and revision

**Files:**
- Generate/update: `poster/poster.pdf`, `poster/preview.png`, `appendix/appendix.pdf`

**Interfaces:**
- Produces visually and programmatically inspected PDFs.

- [ ] Verify poster MediaBox is approximately 594 × 841 mm, portrait, and exactly one page.
- [ ] Render at readable resolution with Poppler; inspect clipping, overlaps, hierarchy, margins, chart labels, and citations.
- [ ] Extract fonts/text to check embedding, mandatory section labels, unresolved markers, and practical 24 pt body target.
- [ ] Revise and repeat until clean; commit with `fix poster layout`.

### Task 14: Reproduction and submission gate

**Files:**
- Update: `README.md`
- Create: `submission/poster.pdf`, `submission/appendix.pdf`

**Interfaces:**
- Produces: final reproducible repository and exactly two submission files.

- [ ] Run `uv sync --frozen --all-groups`, full pytest, Ruff, quick experiment, result/figure regeneration, and clean TeX rebuild.
- [ ] Verify every poster number against `results/final/` and every citation key against `references/references.bib`.
- [ ] Check `submission/` contains exactly the two PDFs; do not create a ZIP without a supplied student ID.
- [ ] Print and store the final checklist in `docs/final_checklist.md` with truthful pass/fail evidence.
- [ ] Commit with `final submission checks` and mark the goal complete only when every required deliverable exists and required gates have passed or are precisely documented as blocked.
