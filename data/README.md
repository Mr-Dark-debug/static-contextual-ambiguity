# Data provenance

`scripts/download_data.py` downloads the WiC portion of the official SuperGLUE v2 release, verifies the frozen archive checksum, extracts only the three expected JSONL files, validates their spans/labels/counts, and writes `processed/dataset_audit.json`.

The WiC dataset is licensed under CC BY-NC 4.0 by its authors. Raw data are deliberately ignored by Git; reproduce them with:

```powershell
uv run python scripts/download_data.py
```

Expected archive SHA-256:

```text
ee7e67f4ae9eafbf533780faa198e62167f3cda54256cdf261877be3c0e90900
```

SuperGLUE's `test.jsonl` has no labels. This project validates it structurally but never reports a local test score.

The GloVe 6B archive is downloaded from Stanford and is likewise ignored by Git. Its verified SHA-256 is:

```text
617afb2fe6cbd085c235baf7a465b96f4112bd7f7ccb2b2cbd649fed9cbcf2fb
```
