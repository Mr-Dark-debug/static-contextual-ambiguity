from pathlib import Path

import matplotlib.image as mpimg
import pandas as pd

from lexical_ambiguity.visualization.figures import (
    model_comparison_data,
    plot_model_comparison,
)


def test_model_comparison_values_match_source_tables() -> None:
    metrics = pd.DataFrame(
        {
            "system": ["bert_mean_last_four", "glove_target", "glove_context_2"],
            "accuracy": [0.67, 0.50, 0.55],
        }
    )
    intervals = pd.DataFrame(
        {
            "system": ["glove_target", "glove_context_2", "bert_mean_last_four"],
            "metric": ["accuracy", "accuracy", "accuracy"],
            "lower": [0.46, 0.51, 0.63],
            "upper": [0.54, 0.59, 0.71],
        }
    )

    data = model_comparison_data(metrics, intervals)

    assert data["system"].tolist() == [
        "glove_target",
        "glove_context_2",
        "bert_mean_last_four",
    ]
    assert data["accuracy"].tolist() == [0.50, 0.55, 0.67]
    assert data["lower"].tolist() == [0.46, 0.51, 0.63]


def test_png_exceeds_150_ppi_at_eight_inch_placement(tmp_path: Path) -> None:
    data = pd.DataFrame(
        {
            "system": ["glove_target", "glove_context_2", "bert_mean_last_four"],
            "accuracy": [0.50, 0.55, 0.67],
            "lower": [0.46, 0.51, 0.63],
            "upper": [0.54, 0.59, 0.71],
            "kind": ["glove_target", "glove_context", "bert"],
            "display": ["target", "context", "BERT"],
            "order": [0, 1, 2],
        }
    )

    plot_model_comparison(data, tmp_path)
    image = mpimg.imread(tmp_path / "model_comparison.png")

    assert image.shape[1] / 8.0 >= 150
    assert (tmp_path / "model_comparison.pdf").exists()
    assert (tmp_path / "model_comparison.svg").exists()
