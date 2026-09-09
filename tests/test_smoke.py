from pathlib import Path

import numpy as np

import lexical_ambiguity.experiment as experiment
from lexical_ambiguity.config import (
    BertConfig,
    DataConfig,
    EvaluationConfig,
    ExperimentConfig,
    GloveConfig,
    LimitConfig,
    OutputConfig,
    RuntimeConfig,
)
from lexical_ambiguity.embeddings.bert import BertRepresentations
from lexical_ambiguity.embeddings.glove import EmbeddingStore
from lexical_ambiguity.types import WicExample


def _rows(split: str, count: int, *, labeled: bool) -> list[WicExample]:
    return [
        WicExample(
            idx=index,
            word="bank",
            sentence1=f"The bank opened branch {index}.",
            sentence2=f"The bank closed branch {index}.",
            start1=4,
            end1=8,
            start2=4,
            end2=8,
            label=bool(index % 2) if labeled else None,
            version="1.1",
            split=split,
        )
        for index in range(count)
    ]


class TinyEncoder:
    def encode(
        self, rows: list[WicExample], *, show_progress: bool = True
    ) -> BertRepresentations:
        del show_progress
        vectors = np.zeros((len(rows), 2, 2), dtype=np.float32)
        vectors[:, :, 0] = 1.0
        for index, row in enumerate(rows):
            if row.label is False:
                vectors[index, 1] = [0.0, 1.0]
        return BertRepresentations(
            vectors={
                **{f"layer_{layer}": vectors.copy() for layer in range(1, 13)},
                "mean_last_four": vectors.copy(),
            },
            wordpiece_counts=np.ones((len(rows), 2), dtype=np.int16),
            device="cpu-test",
            model="tiny",
            revision="test",
        )


def _config(root: Path) -> ExperimentConfig:
    return ExperimentConfig(
        seed=7,
        data=DataConfig(
            url="https://example.test/wic.zip",
            sha256="a" * 64,
            raw_dir=root / "data/raw",
            processed_dir=root / "data/processed",
            train_split="train",
            validation_split="val",
            test_split="test",
        ),
        glove=GloveConfig(
            url="https://example.test/glove.zip",
            sha256=None,
            member="tiny.txt",
            dimensions=2,
            context_windows=(2, 5),
        ),
        bert=BertConfig(
            model="tiny",
            revision="test",
            max_length=32,
            batch_size=4,
            primary_candidates=("layer_12", "mean_last_four"),
        ),
        evaluation=EvaluationConfig(
            tune_holdout_fraction=0.25,
            threshold_objective="macro_f1",
            bootstrap_resamples=10,
            confidence_level=0.95,
        ),
        runtime=RuntimeConfig(device="cpu", deterministic=False, num_workers=0),
        output=OutputConfig(
            cache_dir=root / "cache",
            raw_results_dir=root / "raw",
            final_results_dir=root / "final",
            examples_dir=root / "examples",
            figures_dir=root / "figures",
        ),
        limits=LimitConfig(train=None, validation=None),
        source_path=root / "configs/test.yaml",
        project_root=root,
    )


def test_injected_encoder_pipeline_writes_complete_artifacts(tmp_path, monkeypatch) -> None:
    splits = {
        "train": _rows("train", 20, labeled=True),
        "val": _rows("val", 12, labeled=True),
        "test": _rows("test", 4, labeled=False),
    }
    monkeypatch.setattr(experiment, "ensure_wic_data", lambda **kwargs: tmp_path)
    monkeypatch.setattr(
        experiment, "load_wic_split", lambda processed_dir, split: splits[split]
    )
    monkeypatch.setattr(experiment, "validate_expected_release", lambda audits: None)
    monkeypatch.setattr(experiment, "validate_no_cross_split_pairs", lambda a, b: None)
    monkeypatch.setattr(experiment, "ensure_glove_file", lambda config, raw_dir: tmp_path)
    store = EmbeddingStore({"bank": np.array([1.0, 0.0])}, dimensions=2)
    monkeypatch.setattr(
        experiment.EmbeddingStore,
        "from_text",
        classmethod(lambda cls, path, dimensions, vocabulary: store),
    )

    def fake_static(rows, store, windows):
        del store
        labels = np.asarray([bool(row.label) for row in rows])
        output = {"glove_target": np.ones(len(rows))}
        for index, window in enumerate(windows):
            output[f"glove_context_{window}"] = np.where(
                labels, 0.9 - index * 0.1, 0.1 + index * 0.1
            )
        diagnostics = {
            name: {
                "missing_scores": 0,
                "target_fallback_sides": 0,
                "oov_context_tokens": 0,
            }
            for name in output
        }
        return output, diagnostics

    monkeypatch.setattr(experiment, "_static_scores", fake_static)
    artifacts = experiment.run_experiment(
        _config(tmp_path), bert_encoder_factory=lambda config: TinyEncoder()
    )

    assert artifacts.selection_ledger.exists()
    assert artifacts.metrics.exists()
    assert artifacts.bootstrap_ci.exists()
    with np.load(tmp_path / "cache/bert_train.npz") as buffers:
        assert "layer_12" in buffers.files
    assert len(list((tmp_path / "final").glob("*"))) >= 8
