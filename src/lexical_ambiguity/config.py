"""Validated experiment configuration.

The YAML files are part of the scientific record. Being strict here is useful:
a misspelled key should stop a run, not quietly change the experiment.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypeAlias

import yaml

ContextWindow: TypeAlias = int | Literal["sentence"]


class ConfigError(ValueError):
    """Raised when a configuration cannot describe a valid experiment."""


@dataclass(frozen=True, slots=True)
class DataConfig:
    url: str
    sha256: str
    raw_dir: Path
    processed_dir: Path
    train_split: str
    validation_split: str
    test_split: str


@dataclass(frozen=True, slots=True)
class GloveConfig:
    url: str
    sha256: str | None
    member: str
    dimensions: int
    context_windows: tuple[ContextWindow, ...]


@dataclass(frozen=True, slots=True)
class BertConfig:
    model: str
    revision: str
    max_length: int
    batch_size: int
    primary_candidates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvaluationConfig:
    tune_holdout_fraction: float
    threshold_objective: str
    bootstrap_resamples: int
    confidence_level: float


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    device: Literal["auto", "cpu", "cuda"]
    deterministic: bool
    num_workers: int


@dataclass(frozen=True, slots=True)
class OutputConfig:
    cache_dir: Path
    raw_results_dir: Path
    final_results_dir: Path
    examples_dir: Path
    figures_dir: Path


@dataclass(frozen=True, slots=True)
class LimitConfig:
    train: int | None
    validation: int | None


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    seed: int
    data: DataConfig
    glove: GloveConfig
    bert: BertConfig
    evaluation: EvaluationConfig
    runtime: RuntimeConfig
    output: OutputConfig
    limits: LimitConfig
    source_path: Path
    project_root: Path


_ROOT_KEYS = {
    "seed",
    "data",
    "glove",
    "bert",
    "evaluation",
    "runtime",
    "output",
    "limits",
}


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a mapping")
    return value


def _section(root: dict[str, Any], name: str, expected: set[str]) -> dict[str, Any]:
    section = _mapping(root.get(name), name)
    unknown = set(section) - expected
    missing = expected - set(section)
    if unknown:
        raise ConfigError(f"{name} has unknown keys: {sorted(unknown)}")
    if missing:
        raise ConfigError(f"{name} is missing keys: {sorted(missing)}")
    return section


def _project_path(root: Path, raw: Any, name: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigError(f"{name} must be a non-empty path string")
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _positive_int(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigError(f"{name} must be a positive integer")
    return value


def _optional_limit(value: Any, name: str) -> int | None:
    return None if value is None else _positive_int(value, name)


def load_config(path: str | Path) -> ExperimentConfig:
    """Load a YAML config and resolve project-relative paths.

    The project root is the parent of the ``configs`` directory containing the
    file. Temporary test configs still receive a deterministic parent root.
    """

    source_path = Path(path).resolve()
    try:
        raw = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ConfigError(f"could not load {source_path}: {error}") from error

    root = _mapping(raw, "configuration")
    unknown = set(root) - _ROOT_KEYS
    if unknown:
        raise ConfigError(f"configuration has unknown keys: {sorted(unknown)}")
    missing = _ROOT_KEYS - set(root)
    if missing:
        raise ConfigError(f"configuration is missing keys: {sorted(missing)}")

    project_root = source_path.parent.parent.resolve()
    seed = root["seed"]
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ConfigError("seed must be a non-negative integer")

    data_raw = _section(
        root,
        "data",
        {
            "url",
            "sha256",
            "raw_dir",
            "processed_dir",
            "train_split",
            "validation_split",
            "test_split",
        },
    )
    data_sha = data_raw["sha256"]
    if not isinstance(data_sha, str) or len(data_sha) != 64:
        raise ConfigError("data.sha256 must contain 64 hexadecimal characters")
    try:
        int(data_sha, 16)
    except ValueError as error:
        raise ConfigError("data.sha256 must be hexadecimal") from error
    data = DataConfig(
        url=str(data_raw["url"]),
        sha256=data_sha.lower(),
        raw_dir=_project_path(project_root, data_raw["raw_dir"], "data.raw_dir"),
        processed_dir=_project_path(project_root, data_raw["processed_dir"], "data.processed_dir"),
        train_split=str(data_raw["train_split"]),
        validation_split=str(data_raw["validation_split"]),
        test_split=str(data_raw["test_split"]),
    )

    glove_raw = _section(
        root,
        "glove",
        {"url", "sha256", "member", "dimensions", "context_windows"},
    )
    raw_windows = glove_raw["context_windows"]
    if not isinstance(raw_windows, list) or not raw_windows:
        raise ConfigError("glove.context_windows must be a non-empty list")
    windows: list[ContextWindow] = []
    for value in raw_windows:
        if value == "sentence":
            windows.append("sentence")
        elif isinstance(value, int) and not isinstance(value, bool) and value > 0:
            windows.append(value)
        else:
            raise ConfigError("context windows must be positive integers or 'sentence'")
    if len(set(windows)) != len(windows):
        raise ConfigError("glove.context_windows contains duplicates")
    glove_sha = glove_raw["sha256"]
    if glove_sha is not None and (not isinstance(glove_sha, str) or len(glove_sha) != 64):
        raise ConfigError("glove.sha256 must be null or a 64-character checksum")
    glove = GloveConfig(
        url=str(glove_raw["url"]),
        sha256=glove_sha.lower() if isinstance(glove_sha, str) else None,
        member=str(glove_raw["member"]),
        dimensions=_positive_int(glove_raw["dimensions"], "glove.dimensions"),
        context_windows=tuple(windows),
    )

    bert_raw = _section(
        root,
        "bert",
        {"model", "revision", "max_length", "batch_size", "primary_candidates"},
    )
    candidates = bert_raw["primary_candidates"]
    allowed_candidates = {"layer_12", "mean_last_four"}
    if (
        not isinstance(candidates, list)
        or not candidates
        or not all(isinstance(item, str) for item in candidates)
        or set(candidates) - allowed_candidates
    ):
        raise ConfigError(f"bert.primary_candidates must use {sorted(allowed_candidates)}")
    bert = BertConfig(
        model=str(bert_raw["model"]),
        revision=str(bert_raw["revision"]),
        max_length=_positive_int(bert_raw["max_length"], "bert.max_length"),
        batch_size=_positive_int(bert_raw["batch_size"], "bert.batch_size"),
        primary_candidates=tuple(candidates),
    )

    eval_raw = _section(
        root,
        "evaluation",
        {
            "tune_holdout_fraction",
            "threshold_objective",
            "bootstrap_resamples",
            "confidence_level",
        },
    )
    holdout = float(eval_raw["tune_holdout_fraction"])
    confidence = float(eval_raw["confidence_level"])
    if not 0.0 < holdout < 0.5:
        raise ConfigError("evaluation.tune_holdout_fraction must be between 0 and 0.5")
    if not 0.0 < confidence < 1.0:
        raise ConfigError("evaluation.confidence_level must be between 0 and 1")
    if eval_raw["threshold_objective"] != "macro_f1":
        raise ConfigError("only the prespecified macro_f1 threshold objective is supported")
    evaluation = EvaluationConfig(
        tune_holdout_fraction=holdout,
        threshold_objective="macro_f1",
        bootstrap_resamples=_positive_int(
            eval_raw["bootstrap_resamples"], "evaluation.bootstrap_resamples"
        ),
        confidence_level=confidence,
    )

    runtime_raw = _section(root, "runtime", {"device", "deterministic", "num_workers"})
    device = runtime_raw["device"]
    if device not in {"auto", "cpu", "cuda"}:
        raise ConfigError("runtime.device must be auto, cpu, or cuda")
    deterministic = runtime_raw["deterministic"]
    num_workers = runtime_raw["num_workers"]
    if not isinstance(deterministic, bool):
        raise ConfigError("runtime.deterministic must be boolean")
    if not isinstance(num_workers, int) or isinstance(num_workers, bool) or num_workers < 0:
        raise ConfigError("runtime.num_workers must be a non-negative integer")
    runtime = RuntimeConfig(
        device=device,
        deterministic=deterministic,
        num_workers=num_workers,
    )

    output_raw = _section(
        root,
        "output",
        {"cache_dir", "raw_results_dir", "final_results_dir", "examples_dir", "figures_dir"},
    )
    output = OutputConfig(
        cache_dir=_project_path(project_root, output_raw["cache_dir"], "output.cache_dir"),
        raw_results_dir=_project_path(
            project_root, output_raw["raw_results_dir"], "output.raw_results_dir"
        ),
        final_results_dir=_project_path(
            project_root, output_raw["final_results_dir"], "output.final_results_dir"
        ),
        examples_dir=_project_path(project_root, output_raw["examples_dir"], "output.examples_dir"),
        figures_dir=_project_path(project_root, output_raw["figures_dir"], "output.figures_dir"),
    )

    limits_raw = _section(root, "limits", {"train", "validation"})
    limits = LimitConfig(
        train=_optional_limit(limits_raw["train"], "limits.train"),
        validation=_optional_limit(limits_raw["validation"], "limits.validation"),
    )

    return ExperimentConfig(
        seed=seed,
        data=data,
        glove=glove,
        bert=bert,
        evaluation=evaluation,
        runtime=runtime,
        output=output,
        limits=limits,
        source_path=source_path,
        project_root=project_root,
    )
