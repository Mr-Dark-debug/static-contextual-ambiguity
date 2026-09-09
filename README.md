# Static vs Contextual Embeddings for Lexical Ambiguity

Static embeddings give *bank* one vector forever. Very loyal. Unfortunately, English is not.

This MSc NLP project asks whether the vector for a marked word changes in a useful way when its meaning changes. It compares three frozen representations on Word-in-Context (WiC): GloVe for the target alone, an average of GloVe context words, and the marked target from `bert-base-uncased`.

The experiment is being built science-first: source verification, validated spans, train-only selection, held-out results, uncertainty, and error analysis come before the poster. Reproduction commands and final measured results will be added as each stage passes its checks.

## Current protocol

- Official SuperGLUE v2 WiC: 5,428 train, 638 held-out validation, 1,400 unlabeled test.
- Training data alone selects context window, BERT representation, and decision thresholds.
- Validation is opened only after those decisions are frozen.
- The unlabeled SuperGLUE test set receives no invented score.

See [the experiment design](docs/experiment_design.md), [literature matrix](docs/literature_matrix.md), and [decision log](docs/decisions.md).

## Environment

```powershell
uv sync --all-groups
uv run pytest
uv run ruff check .
```

Python 3.11 is pinned in `.python-version`. On Windows, the lock uses PyTorch's CUDA 13.0 wheel; the same wheel can fall back to CPU when CUDA is unavailable.
