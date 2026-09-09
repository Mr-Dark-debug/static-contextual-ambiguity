from pathlib import Path

import pytest

from lexical_ambiguity.config import ConfigError, load_config

ROOT = Path(__file__).resolve().parents[1]


def test_default_config_captures_frozen_protocol() -> None:
    config = load_config(ROOT / "configs" / "default.yaml")

    assert config.seed == 2026
    assert config.data.train_split == "train"
    assert config.data.validation_split == "val"
    assert config.glove.dimensions == 300
    assert config.glove.context_windows == (2, 5, 10, "sentence")
    assert config.bert.model == "google-bert/bert-base-uncased"
    assert config.bert.primary_candidates == ("layer_12", "mean_last_four")
    assert config.evaluation.bootstrap_resamples == 1000
    assert config.output.final_results_dir == ROOT / "results" / "final"


def test_quick_config_limits_both_labeled_splits() -> None:
    config = load_config(ROOT / "configs" / "quick_test.yaml")

    assert config.limits.train == 96
    assert config.limits.validation == 64
    assert config.bert.batch_size == 8


def test_unknown_top_level_key_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("seed: 2026\nsurprise: nope\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="unknown keys"):
        load_config(config_path)
