"""Run the bounded, real-model pipeline smoke test."""

from lexical_ambiguity.experiment import run_experiment

if __name__ == "__main__":
    artifacts = run_experiment("configs/quick_test.yaml")
    print(f"Quick metrics: {artifacts.metrics}")
