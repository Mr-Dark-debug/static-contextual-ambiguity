"""Generate all poster figures from frozen saved results."""

from pathlib import Path

from lexical_ambiguity.visualization.figures import generate_all_figures

if __name__ == "__main__":
    generate_all_figures(
        results_dir=Path("results/final"),
        raw_dir=Path("results/raw"),
        examples_dir=Path("results/examples"),
        output_dir=Path("figures"),
    )
    print("Wrote PDF, SVG, and 300-PPI PNG figure sets to figures/")
