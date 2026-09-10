# Static vs Contextual Embeddings for Lexical Ambiguity: A Word-in-Context Evaluation

Static embeddings give *bank* one vector forever. Very loyal. Unfortunately, English is
not. This MSc NLP project evaluates whether a marked word's representation changes in a
useful way when its meaning changes.

The experiment compares three frozen, cosine-thresholded representations on the official
SuperGLUE v2 Word-in-Context (WiC) split:

1. the same GloVe target vector on both sides (a diagnostic);
2. the mean of nearby GloVe context vectors, excluding the target;
3. the offset-aligned BERT target representation from `bert-base-uncased`.

All choices and thresholds are selected using training data only. The 638 labeled
validation pairs are evaluated once; the 1,400-row public test split is unlabeled and no
test score is invented.

## Main result

| Frozen system | Validation accuracy | Macro F1 | ROC-AUC |
|---|---:|---:|---:|
| GloVe target diagnostic | 0.5000 | 0.3333 | 0.5000 |
| GloVe context, selected window $\pm 2$ | 0.5549 | 0.5511 | 0.5800 |
| BERT target, selected mean of last four layers | **0.6708** | **0.6673** | **0.7163** |

BERT adds 0.1160 accuracy over local GloVe context. In 1,000 paired bootstrap
resamples, the 95% interval for **GloVe context minus BERT** is
[-0.1693, -0.0658]. This is a result under the locked sample and protocol, not a claim
that one representation universally dominates another. Layer analysis and 210 BERT
errors further qualify the conclusion.

The interpretation is in [docs/results_interpretation.md](docs/results_interpretation.md),
and every displayed number is traceable to the committed CSV/JSON artifacts in
`results/`.

## Reproduce the experiment

Requirements: Python 3.11, [uv](https://docs.astral.sh/uv/), enough storage for GloVe and
the Hugging Face model cache, and preferably a CUDA GPU. The code has a CPU path.

```powershell
uv sync --frozen --all-groups
uv run pytest -q
uv run ruff check .

uv run python scripts/download_data.py
uv run python scripts/run_quick_test.py
uv run python scripts/run_experiment.py
uv run python scripts/analyse_results.py
uv run python scripts/generate_figures.py
```

`download_data.py` verifies the WiC archive SHA-256 and all split counts/spans. The full
run also downloads and verifies GloVe 6B, pins the BERT model revision, records the
runtime, and caches expensive arrays using dataset/model/config metadata. Repeated runs
reuse a cache only when its metadata match.

The measured full run used Python 3.11.15, PyTorch 2.11.0+cu130, Transformers 5.17.0,
and an NVIDIA GeForce RTX 3050 Ti Laptop GPU. Its clean source revision is recorded in
`results/final/environment.json`; a later cached reproduction regenerated the same
artifacts. On that machine, a full cache-integrity rerun took about 18 seconds. A batch of
the 16 longest training pairs peaked at 469 MiB allocated / 492 MiB reserved CUDA memory,
including the loaded model; driver overhead is additional. The checked workspace used
1.77 GiB for source archives, 0.44 GiB for experiment caches, and 0.41 GiB in the external
Hugging Face model cache (about 2.62 GiB total). A first run also depends on download speed
and should be budgeted in tens of minutes; only the cache-hit timing is directly measured.

## Build and verify the documents

Install or locate [Tectonic](https://tectonic-typesetting.github.io/) 0.17 or compatible,
then pass its executable explicitly. This regenerates all LaTeX data, compiles the
unsigned declaration, poster, and appendix in dependency order, and stages exactly two
PDFs.

```powershell
$tectonic = "C:\path\to\tectonic.exe"
uv run python scripts/build_submission.py --compile --stage --tectonic $tectonic
uv run python scripts/verify_submission.py
```

The verifier checks byte identity with the built sources, exact submission contents,
page counts, A1/A4 media boxes, required extractable headings, and embedded fonts
(including Type 3 glyph programs inside vector figures).

After obtaining the real signed declaration, pass it without editing or forging metadata:

```powershell
uv run python scripts/build_submission.py --compile --stage --tectonic $tectonic `
  --declaration "C:\path\to\signed-declaration.pdf"
uv run python scripts/verify_submission.py --signed
```

## Project map

- `configs/default.yaml` — frozen full protocol; `configs/quick_test.yaml` — bounded
  real-model smoke run.
- `src/lexical_ambiguity/` — loaders, static/contextual encoders, caching, selection,
  metrics, bootstrap, analysis, and plots.
- `results/raw/selection_ledger.json` — train-only candidate decision and integrity hash.
- `results/final/` — predictions, metrics, intervals, layers, diagnostics, and environment.
- `figures/` — code-generated PDF, PNG, and SVG figures.
- `poster/poster.tex` and `appendix/appendix.tex` — source documents.
- `submission/poster.pdf` and `submission/appendix.pdf` — the only staged deliverables.
- `docs/final_checklist.md` — final gate evidence and the remaining personalisation step.

## Before personal submission

The repository intentionally does not invent a student name, ID, institutional
declaration, signature, or repository URL. Replace the clearly marked author/repository
placeholders in `poster/poster.tex` and `appendix/appendix.tex`, replace
`appendix/integrity_declaration_PLACEHOLDER.tex` with the institution-approved wording,
sign it yourself, rebuild with `--declaration`, and rerun the verifier in `--signed` mode.

WiC is CC BY-NC 4.0 according to its authors. Raw datasets, GloVe vectors, model weights,
and embedding caches are excluded from Git; upstream terms still apply. Detailed data
provenance and frozen checksums are in [data/README.md](data/README.md).
