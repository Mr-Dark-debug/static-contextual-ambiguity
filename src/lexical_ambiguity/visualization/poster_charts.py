"""Plain-language poster charts from the frozen validation predictions."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lexical_ambiguity.visualization.figures import _save_all, model_comparison_data

INK = "#182E42"
BLUE = "#007AC3"
ORANGE = "#C55A11"
GRAY = "#84929D"


def paired_outcome_data(predictions: pd.DataFrame) -> pd.DataFrame:
    """Partition primary-system outcomes without conditioning on the diagnostic."""
    columns = ["bert_mean_last_four_correct", "glove_context_2_correct"]
    if predictions.empty or predictions[columns].isna().any().any():
        raise ValueError("complete paired predictions are required")
    if any(predictions[column].dtype != bool for column in columns):
        raise ValueError("correctness columns must contain boolean values")
    bert, glove = (predictions[column] for column in columns)
    return pd.DataFrame(
        {
            "outcome": [
                "Both correct",
                "Only BERT correct",
                "Only GloVe correct",
                "Neither correct",
            ],
            "count": [
                int((bert & glove).sum()),
                int((bert & ~glove).sum()),
                int((~bert & glove).sum()),
                int((~bert & ~glove).sum()),
            ],
        }
    )


def plot_poster_accuracy(data: pd.DataFrame, metrics: pd.DataFrame, output: Path) -> None:
    """Direct labels, a full percentage scale and bootstrap uncertainty."""
    figure = plt.figure(figsize=(14, 3.2), facecolor="white")
    axis = figure.add_axes((0.34, 0.20, 0.44, 0.76))
    labels = [
        ("GloVe: word only", "One fixed vector for the target word"),
        ("GloVe: nearby words", "Average of nearby word vectors"),
        ("BERT: word in its sentence", "Target vector changes with context"),
    ]
    metrics = metrics.set_index("system")
    for row, y, color, (label, explanation) in zip(
        data.itertuples(index=False), [2, 1, 0], [GRAY, BLUE, ORANGE], labels, strict=True
    ):
        value = row.accuracy * 100
        axis.errorbar(
            value,
            y,
            xerr=[[value - row.lower * 100], [row.upper * 100 - value]],
            fmt="o",
            markersize=11,
            color=color,
            ecolor=color,
            elinewidth=2.3,
            capsize=6,
        )
        yf = 0.20 + 0.76 * ((y + 0.5) / 3)
        figure.text(0.005, yf + 0.035, label, fontsize=20, weight="bold", color=INK, va="center")
        figure.text(0.005, yf - 0.045, explanation, fontsize=15, color=INK, va="center")
        record = metrics.loc[row.system]
        correct = int(record["tn"] + record["tp"])
        figure.text(0.815, yf + 0.028, f"{value:.1f}%", fontsize=24, weight="bold", color=color)
        figure.text(
            0.815, yf - 0.047, f"{correct} / {int(record['count'])} correct", fontsize=17, color=INK
        )
    axis.axvline(50, linestyle=(0, (3, 4)), color=GRAY, linewidth=1.2)
    axis.set(xlim=(0, 100), ylim=(-0.5, 2.5), yticks=[], xticks=np.arange(0, 101, 25))
    axis.set_xlabel("Correct answers (%)", fontsize=18, labelpad=10, color=INK)
    axis.tick_params(axis="x", labelsize=17, length=4, colors=INK)
    axis.spines[["top", "left", "right"]].set_visible(False)
    axis.spines["bottom"].set_color(GRAY)
    axis.grid(axis="x", color="#E6EBEF", linewidth=0.7)
    axis.set_axisbelow(True)
    _save_all(figure, output, "poster_accuracy", background="white")


def plot_paired_outcomes(data: pd.DataFrame, output: Path) -> None:
    figure = plt.figure(figsize=(7.4, 3.0), facecolor="white")
    axis = figure.add_axes((0.43, 0.19, 0.48, 0.77))
    values = data["count"].to_numpy()
    positions = np.arange(len(data))[::-1]
    axis.barh(positions, values, height=0.52, color=[INK, ORANGE, BLUE, GRAY])
    for y, value, label in zip(positions, values, data["outcome"], strict=True):
        axis.text(
            -0.06,
            y,
            label,
            transform=axis.get_yaxis_transform(),
            ha="right",
            va="center",
            fontsize=17,
            color=INK,
        )
        axis.text(value + 8, y, str(value), va="center", fontsize=21, weight="bold", color=INK)
    axis.set(xlim=(0, max(values) * 1.21), ylim=(-0.6, 3.6), yticks=[])
    axis.set_xlabel("Number of sentence pairs", fontsize=17, labelpad=10, color=INK)
    axis.set_xticks([0, 100, 200, 300])
    axis.tick_params(axis="x", labelsize=16, colors=INK)
    axis.spines[["top", "left", "right"]].set_visible(False)
    axis.spines["bottom"].set_color(GRAY)
    _save_all(figure, output, "poster_outcomes", background="white")


def generate_poster_charts(results_dir: Path, output_dir: Path) -> None:
    metrics = pd.read_csv(results_dir / "metrics.csv")
    intervals = pd.read_csv(results_dir / "bootstrap_ci.csv")
    predictions = pd.read_csv(results_dir / "predictions.csv")
    outcomes = paired_outcome_data(predictions)
    plot_poster_accuracy(model_comparison_data(metrics, intervals), metrics, output_dir)
    plot_paired_outcomes(outcomes, output_dir)
