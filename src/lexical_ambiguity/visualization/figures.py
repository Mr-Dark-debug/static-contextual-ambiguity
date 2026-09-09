"""Publication figures generated only from frozen result artifacts."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

BACKGROUND = "#F7F4ED"
INK = "#17324D"
COLORS = {
    "glove_target": "#B8B8B8",
    "glove_context": "#0072B2",
    "bert": "#D55E00",
    "different": "#CC79A7",
    "same": "#009E73",
}


def _system_kind(name: str) -> str:
    if name == "glove_target":
        return "glove_target"
    if name.startswith("glove_context_"):
        return "glove_context"
    if name.startswith("bert_"):
        return "bert"
    raise ValueError(f"unrecognized system: {name}")


def _display_name(name: str) -> str:
    if name == "glove_target":
        return "GloVe target\n(no context)"
    if name.startswith("glove_context_"):
        suffix = name.removeprefix("glove_context_")
        return f"GloVe context\n(±{suffix} tokens)"
    if name == "bert_mean_last_four":
        return "BERT target\n(mean last 4)"
    return name.replace("_", " ")


def model_comparison_data(
    metrics: pd.DataFrame, intervals: pd.DataFrame
) -> pd.DataFrame:
    accuracy_ci = intervals.loc[
        intervals["metric"] == "accuracy", ["system", "lower", "upper"]
    ]
    merged = metrics[["system", "accuracy"]].merge(
        accuracy_ci, on="system", validate="one_to_one"
    )
    order = {"glove_target": 0, "glove_context": 1, "bert": 2}
    merged["kind"] = merged["system"].map(_system_kind)
    merged["display"] = merged["system"].map(_display_name)
    merged["order"] = merged["kind"].map(order)
    return merged.sort_values("order").reset_index(drop=True)


def _style_axes(axis: plt.Axes) -> None:
    axis.set_facecolor(BACKGROUND)
    axis.tick_params(colors=INK, labelsize=11)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color(INK)
    axis.xaxis.label.set_color(INK)
    axis.yaxis.label.set_color(INK)
    axis.title.set_color(INK)


def _save_all(figure: Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("pdf", "svg"):
        figure.savefig(
            output_dir / f"{stem}.{suffix}",
            bbox_inches="tight",
            facecolor=BACKGROUND,
        )
    figure.savefig(
        output_dir / f"{stem}.png",
        dpi=300,
        bbox_inches="tight",
        facecolor=BACKGROUND,
    )
    plt.close(figure)


def plot_model_comparison(data: pd.DataFrame, output_dir: Path) -> None:
    figure, axis = plt.subplots(figsize=(8.0, 5.0), facecolor=BACKGROUND)
    positions = np.arange(len(data))
    values = data["accuracy"].to_numpy()
    errors = np.vstack(
        (values - data["lower"].to_numpy(), data["upper"].to_numpy() - values)
    )
    bars = axis.bar(
        positions,
        values,
        yerr=errors,
        width=0.68,
        color=[COLORS[kind] for kind in data["kind"]],
        edgecolor=INK,
        linewidth=0.8,
        capsize=5,
    )
    axis.axhline(0.5, color=INK, linestyle=(0, (4, 4)), linewidth=1.2, alpha=0.65)
    axis.text(2.45, 0.505, "balanced chance", color=INK, ha="right", va="bottom")
    for bar, value in zip(bars, values, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.025,
            f"{value * 100:.1f}%",
            ha="center",
            va="bottom",
            color=INK,
            fontsize=14,
            fontweight="bold",
        )
    axis.annotate(
        "+11.6 points",
        xy=(2, values[2]),
        xytext=(1.18, 0.79),
        color=COLORS["bert"],
        fontsize=14,
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": COLORS["bert"], "lw": 1.8},
    )
    axis.set_xticks(positions, data["display"])
    axis.set_ylim(0.42, 0.82)
    axis.set_ylabel("Validation accuracy")
    axis.set_title(
        "Contextual target vectors make the strongest distinction",
        loc="left",
        fontsize=17,
        fontweight="bold",
        pad=14,
    )
    axis.text(
        0.0,
        -0.22,
        "Error bars: fixed-seed percentile 95% bootstrap intervals; n = 638 pairs.",
        transform=axis.transAxes,
        color=INK,
        fontsize=10,
    )
    _style_axes(axis)
    figure.tight_layout()
    _save_all(figure, output_dir, "model_comparison")


def plot_similarity_distributions(scores: pd.DataFrame, output_dir: Path) -> None:
    validation = scores.loc[scores["split"] == "validation"].copy()
    static = next(column for column in validation if column.startswith("glove_context_"))
    # Raw scores contain every candidate; use the frozen primary names explicitly.
    static = "glove_context_2" if "glove_context_2" in validation else static
    bert = "bert_mean_last_four"
    figure, axes = plt.subplots(1, 2, figsize=(9.0, 4.6), facecolor=BACKGROUND)
    for axis, system, title in (
        (axes[0], static, "GloVe ±2 context"),
        (axes[1], bert, "BERT mean last 4"),
    ):
        different = validation.loc[~validation["label"].astype(bool), system]
        same = validation.loc[validation["label"].astype(bool), system]
        bins = np.linspace(
            min(different.min(), same.min()), max(different.max(), same.max()), 23
        )
        axis.hist(
            different,
            bins=bins,
            density=True,
            alpha=0.52,
            color=COLORS["different"],
            label="Different sense",
        )
        axis.hist(
            same,
            bins=bins,
            density=True,
            alpha=0.52,
            color=COLORS["same"],
            label="Same sense",
        )
        axis.set_title(title, loc="left", fontsize=15, fontweight="bold")
        axis.set_xlabel("Cosine similarity")
        _style_axes(axis)
    axes[0].set_ylabel("Density")
    axes[1].legend(frameon=False, fontsize=10, labelcolor=INK)
    figure.suptitle(
        "BERT shifts same-sense pairs toward higher similarity",
        x=0.07,
        ha="left",
        color=INK,
        fontsize=17,
        fontweight="bold",
    )
    figure.tight_layout(rect=(0, 0, 1, 0.92))
    _save_all(figure, output_dir, "similarity_distributions")


def plot_layer_analysis(
    layers: pd.DataFrame, metrics: pd.DataFrame, output_dir: Path
) -> None:
    layer_numbers = layers["system"].str.removeprefix("layer_").astype(int)
    primary = metrics.loc[metrics["system"] == "bert_mean_last_four"].iloc[0]
    figure, axis = plt.subplots(figsize=(8.0, 4.8), facecolor=BACKGROUND)
    axis.plot(
        layer_numbers,
        layers["accuracy"],
        marker="o",
        linewidth=2.4,
        color=COLORS["bert"],
        label="Individual-layer accuracy",
    )
    axis.plot(
        layer_numbers,
        layers["roc_auc"],
        marker="s",
        linewidth=1.8,
        color=COLORS["glove_context"],
        label="Individual-layer ROC-AUC",
    )
    axis.axhline(
        primary["accuracy"],
        color=INK,
        linestyle=(0, (5, 4)),
        linewidth=1.5,
        label=f"Frozen mean-last-four accuracy ({primary['accuracy']:.3f})",
    )
    axis.set_xticks(range(1, 13))
    axis.set_xlabel("BERT layer")
    axis.set_ylabel("Validation score")
    axis.set_ylim(0.54, 0.75)
    axis.set_title(
        "Sense signal builds through middle-to-late layers",
        loc="left",
        fontsize=17,
        fontweight="bold",
    )
    axis.legend(frameon=False, fontsize=10, labelcolor=INK, loc="lower right")
    _style_axes(axis)
    figure.tight_layout()
    _save_all(figure, output_dir, "layer_analysis")


def plot_qualitative_cases(cases: pd.DataFrame, output_dir: Path) -> None:
    success = cases.loc[cases["case_type"] == "bert_only_correct"].iloc[0]
    failure = cases.loc[cases["case_type"] == "bert_high_confidence_error"].iloc[0]
    figure, axes = plt.subplots(1, 2, figsize=(11.0, 3.8), facecolor=BACKGROUND)
    for axis, row, heading, accent in (
        (axes[0], success, "BERT sees the shared sense", COLORS["same"]),
        (axes[1], failure, "A confident miss", COLORS["bert"]),
    ):
        axis.set_facecolor(BACKGROUND)
        axis.axis("off")
        axis.text(
            0.02,
            0.95,
            heading,
            transform=axis.transAxes,
            color=accent,
            fontsize=15,
            fontweight="bold",
            va="top",
        )
        sentences = f"1  {row['sentence1']}\n2  {row['sentence2']}"
        wrapped = "\n".join(textwrap.fill(line, width=48) for line in sentences.splitlines())
        axis.text(
            0.02,
            0.76,
            wrapped,
            transform=axis.transAxes,
            color=INK,
            fontsize=11,
            va="top",
            linespacing=1.5,
        )
        truth = "same" if bool(row["label"]) else "different"
        bert_prediction = (
            "same" if bool(row["bert_mean_last_four_prediction"]) else "different"
        )
        static_prediction = (
            "same" if bool(row["glove_context_2_prediction"]) else "different"
        )
        axis.text(
            0.02,
            0.27,
            f"Gold: {truth}\nBERT: {bert_prediction} "
            f"({row['bert_mean_last_four_score']:.2f})\n"
            f"GloVe: {static_prediction} ({row['glove_context_2_score']:.2f})",
            transform=axis.transAxes,
            color=INK,
            fontsize=11,
            va="top",
        )
        axis.add_patch(
            plt.Rectangle(
                (0, 0),
                1,
                1,
                transform=axis.transAxes,
                fill=False,
                edgecolor=accent,
                linewidth=2,
            )
        )
    figure.suptitle(
        "Context helps—until closely related usages cross the decision boundary",
        x=0.04,
        ha="left",
        color=INK,
        fontsize=17,
        fontweight="bold",
    )
    figure.tight_layout(rect=(0, 0, 1, 0.88))
    _save_all(figure, output_dir, "qualitative_cases")


def generate_all_figures(
    *, results_dir: Path, raw_dir: Path, examples_dir: Path, output_dir: Path
) -> None:
    metrics = pd.read_csv(results_dir / "metrics.csv")
    intervals = pd.read_csv(results_dir / "bootstrap_ci.csv")
    layers = pd.read_csv(results_dir / "layer_metrics.csv")
    scores = pd.read_csv(raw_dir / "scores.csv")
    cases = pd.read_csv(examples_dir / "error_cases.csv")
    plot_model_comparison(model_comparison_data(metrics, intervals), output_dir)
    plot_similarity_distributions(scores, output_dir)
    plot_layer_analysis(layers, metrics, output_dir)
    plot_qualitative_cases(cases, output_dir)

