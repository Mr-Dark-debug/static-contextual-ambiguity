"""Run the complete prespecified WiC experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from lexical_ambiguity.experiment import run_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/default.yaml"))
    arguments = parser.parse_args()
    artifacts = run_experiment(arguments.config)
    print(f"Selection ledger: {artifacts.selection_ledger}")
    print(f"Metrics: {artifacts.metrics}")


if __name__ == "__main__":
    main()

