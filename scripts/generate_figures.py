"""Generate all poster figures from frozen saved results."""

from pathlib import Path

from lexical_ambiguity.visualization.figures import generate_all_figures
from lexical_ambiguity.visualization.poster_charts import generate_poster_charts

if __name__ == "__main__":
    generate_all_figures(
        results_dir=Path("results/final"),
        raw_dir=Path("results/raw"),
        examples_dir=Path("results/examples"),
        output_dir=Path("figures"),
    )
    generate_poster_charts(Path("results/final"), Path("figures"))
    print("Wrote PDF, SVG, and 300-PPI PNG figure sets to figures/")
