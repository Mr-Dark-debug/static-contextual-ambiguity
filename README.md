# Static vs Contextual Embeddings for Lexical Ambiguity

This project evaluates whether contextual word representations distinguish
same-sense and different-sense uses of a word more effectively than static
representations. It uses the Word-in-Context (WiC) task from SuperGLUE and
compares three frozen, similarity-based systems:

- GloVe representation of the target word only.
- GloVe context representation, formed by averaging nearby word vectors.
- BERT target representation, extracted from the full sentence context.

This is a controlled representation probe. The models are pretrained and
frozen; no task fine-tuning is performed.

## Results

The committed full run evaluates 638 labelled WiC validation examples. The
threshold for each system is selected from the training split using the
prespecified protocol in `lexical_ambiguity/experiment.py`.

| System | Accuracy | Macro F1 | Correct |
| --- | ---: | ---: | ---: |
| GloVe target word | 50.0% | 33.3% | 319 / 638 |
| GloVe context window 2 | 55.5% | 55.1% | 354 / 638 |
| BERT mean of last four layers | 67.1% | 66.7% | 428 / 638 |

The results are descriptive of this frozen-embedding protocol and dataset;
they are not a claim that BERT solves lexical ambiguity or that these systems
represent task-specific state of the art. The local WiC test split has no
labels, so this repository does not report a test score.

## Project structure

```text
download_data.py          Download and validate the WiC release
configs/default.yaml      Full experiment configuration
configs/quick_test.yaml   Small smoke-test configuration
lexical_ambiguity/        Experiment, embedding, data, and evaluation code
data/                     Processed data and local downloaded/cache files
results/raw/              Raw scores and candidate-selection ledger
results/final/            Metrics, predictions, confidence intervals, and diagnostics
poster_and_appendix/      Editable poster and appendix LaTeX sources
assets/                   Supporting poster assets
submission/               Submission PDFs, when generated locally
```

Large downloads and model files are intentionally not committed. The checked-
in result files are evidence from the recorded full and quick runs.

## Requirements

- Windows, macOS, or Linux
- Python 3.11 (the project requires `>=3.11,<3.12`)
- [uv](https://docs.astral.sh/uv/)
- Internet access for the first data/model download
- Enough disk space for the WiC archive, GloVe 6B vectors, and BERT weights

CUDA is optional. The default configuration uses `device: auto` and can run on
CPU, although BERT encoding is slower without a compatible GPU.

## Installation

From the repository root:

```powershell
uv sync --frozen --all-groups
```

The project uses the dependencies declared in `pyproject.toml`. On Windows,
the lock file selects the configured PyTorch CUDA index when applicable.

## Download and validate data

Download the official SuperGLUE WiC archive, verify its SHA-256 checksum, and
write the processed split files and audit report:

```powershell
uv run python download_data.py --config configs/default.yaml
```

The source data are downloaded from the URL in the configuration. WiC labels
are available for the train and validation splits, but not for the public test
split. See [data/README.md](data/README.md) for provenance and licensing.

## Run the experiment

Run a bounded smoke test first:

```powershell
uv run python -c "from lexical_ambiguity.experiment import run_experiment; run_experiment('configs/quick_test.yaml')"
```

The smoke test uses 96 training examples and 64 validation examples. Its
outputs are written under `data/cache/quick`, `results/raw/quick`, and
`results/final/quick`.

Run the full protocol with:

```powershell
uv run python -c "from lexical_ambiguity.experiment import run_experiment; run_experiment('configs/default.yaml')"
```

The full configuration uses all 5,428 training examples and 638 validation
examples. It writes the following main artifacts:

- `results/raw/scores.csv`: raw similarity scores.
- `results/raw/selection_ledger.json`: train-only candidate selection record.
- `results/final/metrics.csv`: accuracy, macro F1, precision, recall, ROC AUC,
	and confusion-matrix counts.
- `results/final/predictions.csv`: validation predictions and source examples.
- `results/final/bootstrap_ci.csv`: bootstrap confidence intervals.
- `results/final/paired_differences.csv`: paired system comparisons.
- `results/final/layer_metrics.csv`: BERT layer-by-layer metrics.
- `results/final/run_diagnostics.json`: dataset, cache, device, and runtime
	diagnostics.

Cached representations are reused only when their metadata match the current
dataset, model revision, configuration, and example fingerprints.

## Poster and appendix

The editable LaTeX sources are in [poster_and_appendix](poster_and_appendix):

- [poster.tex](poster_and_appendix/poster.tex)
- [appendix.tex](poster_and_appendix/appendix.tex)
- [authors.tex](poster_and_appendix/authors.tex)

The appendix uses [generated_tables.tex](poster_and_appendix/generated_tables.tex)
and includes the two signed declarations at the repository root. The staged
[appendix PDF](submission/appendix.pdf) ends with those two signed pages. To
rebuild it with Tectonic, run this from `poster_and_appendix/`:

```powershell
tectonic -X compile --outdir ../submission --outfmt pdf --untrusted appendix.tex
```

The poster source still needs its generated result input for a local rebuild.
The existing [poster PDF](submission/poster.pdf) remains in `submission/`.
The hand-in archive [1910474_1911272.zip](submission/1910474_1911272.zip)
contains exactly `poster.pdf` and `appendix.pdf`.

## Reproducibility notes

- The random seed is `2026` in both configurations.
- The full run uses `google-bert/bert-base-uncased` at the revision pinned in
	`configs/default.yaml`.
- GloVe uses the 300-dimensional `glove.6B.300d.txt` file.
- Thresholds are selected on training data with macro F1 as the objective.
- Bootstrap intervals use 1,000 resamples in the full configuration and 100
	resamples in the quick configuration.

The repository contains the implementation and recorded outputs needed to
inspect the analysis. Upstream dataset, embedding, and model licenses remain
applicable.
