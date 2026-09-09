"""Create traceable error partitions and compact descriptive summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from lexical_ambiguity.evaluation.analysis import (
    error_focus_partitions,
    outcome_partitions,
)
from lexical_ambiguity.utils import atomic_write_json


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.casefold().map({"true": True, "false": False}).astype(bool)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("results/final"))
    parser.add_argument("--examples", type=Path, default=Path("results/examples"))
    arguments = parser.parse_args()

    predictions = pd.read_csv(arguments.results / "predictions.csv")
    metrics = pd.read_csv(arguments.results / "metrics.csv")
    paired = pd.read_csv(arguments.results / "paired_differences.csv")
    systems = metrics["system"].astype(str).tolist()
    static = next(name for name in systems if name.startswith("glove_context_"))
    bert = next(name for name in systems if name.startswith("bert_"))
    thresholds = dict(zip(metrics["system"], metrics["threshold"], strict=True))

    for system in systems:
        predictions[f"{system}_prediction"] = _bool_series(
            predictions[f"{system}_prediction"]
        )
        predictions[f"{system}_correct"] = _bool_series(
            predictions[f"{system}_correct"]
        )
    predictions["label"] = _bool_series(predictions["label"])
    predictions["surface_mismatch"] = (
        predictions["target1"].str.casefold() != predictions["word"].str.casefold()
    ) | (predictions["target2"].str.casefold() != predictions["word"].str.casefold())
    predictions["same_surface"] = (
        predictions["target1"].str.casefold()
        == predictions["target2"].str.casefold()
    )
    predictions["sentence_length_gap"] = (
        predictions["sentence1"].str.split().str.len()
        - predictions["sentence2"].str.split().str.len()
    ).abs()
    correct_columns = [f"{system}_correct" for system in systems]
    predictions["outcome_partition"] = outcome_partitions(
        predictions,
        static_correct=f"{static}_correct",
        bert_correct=f"{bert}_correct",
        all_correct_columns=correct_columns,
    )
    predictions["bert_margin"] = np.abs(
        predictions[f"{bert}_score"] - thresholds[bert]
    )
    predictions["bert_error_focus"] = error_focus_partitions(
        predictions[f"{bert}_score"],
        predictions["label"],
        threshold=float(thresholds[bert]),
    )

    def grouped_accuracy(column: str) -> dict[str, list[dict[str, object]]]:
        output: dict[str, list[dict[str, object]]] = {}
        for system in systems:
            rows: list[dict[str, object]] = []
            for group, values in predictions.groupby(column, dropna=False):
                rows.append(
                    {
                        "group": str(group),
                        "count": len(values),
                        "accuracy": float(values[f"{system}_correct"].mean()),
                    }
                )
            output[system] = rows
        return output

    summary = {
        "systems": systems,
        "thresholds": {name: float(value) for name, value in thresholds.items()},
        "partition_counts": {
            str(name): int(count)
            for name, count in predictions["outcome_partition"].value_counts().items()
        },
        "bert_error_focus_counts": {
            str(name): int(count)
            for name, count in predictions["bert_error_focus"].value_counts().items()
        },
        "accuracy_by_label": grouped_accuracy("label"),
        "accuracy_by_surface_mismatch": grouped_accuracy("surface_mismatch"),
        "accuracy_by_same_surface": grouped_accuracy("same_surface"),
        "bert_error_margin_75th_percentile": float(
            predictions.loc[~predictions[f"{bert}_correct"], "bert_margin"].quantile(0.75)
        ),
        "most_frequent_bert_error_words": [
            {"word": str(word), "count": int(count)}
            for word, count in predictions.loc[
                ~predictions[f"{bert}_correct"], "word"
            ]
            .value_counts()
            .head(10)
            .items()
        ],
        "paired_differences": paired.to_dict(orient="records"),
    }

    selections: list[pd.DataFrame] = []
    outcome_specs = {
        "bert_only_correct": "bert_only_correct",
        "static_only_correct": "static_only_correct",
        "all_wrong": "all_wrong",
    }
    for case_type, partition in outcome_specs.items():
        selected = (
            predictions.loc[predictions["outcome_partition"] == partition]
            .sort_values(["bert_margin", "idx"], ascending=[False, True])
            .head(5)
            .copy()
        )
        selected.insert(0, "case_type", case_type)
        selections.append(selected)
    for case_type, focus, ascending in (
        ("bert_high_confidence_error", "high_confidence_error", False),
        ("bert_borderline_error", "borderline_error", True),
    ):
        selected = (
            predictions.loc[predictions["bert_error_focus"] == focus]
            .sort_values(["bert_margin", "idx"], ascending=[ascending, True])
            .head(5)
            .copy()
        )
        selected.insert(0, "case_type", case_type)
        selections.append(selected)

    columns = [
        "case_type",
        "idx",
        "word",
        "target1",
        "target2",
        "sentence1",
        "sentence2",
        "label",
        "surface_mismatch",
        "same_surface",
        "outcome_partition",
        "bert_error_focus",
        "bert_margin",
        *[f"{system}_score" for system in systems],
        *[f"{system}_prediction" for system in systems],
        *correct_columns,
    ]
    cases = pd.concat(selections, ignore_index=True)[columns]
    arguments.examples.mkdir(parents=True, exist_ok=True)
    cases.to_csv(arguments.examples / "error_cases.csv", index=False, lineterminator="\n")
    atomic_write_json(arguments.results / "analysis_summary.json", summary)
    print(f"Wrote {len(cases)} qualitative rows and {len(predictions)}-row summary")


if __name__ == "__main__":
    main()
