"""Download and validate the frozen WiC release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lexical_ambiguity.config import load_config
from lexical_ambiguity.data import (
    audit_examples,
    ensure_wic_data,
    load_wic_split,
    validate_expected_release,
    validate_no_cross_split_pairs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/default.yaml"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    extracted = ensure_wic_data(
        url=config.data.url,
        expected_sha256=config.data.sha256,
        raw_dir=config.data.raw_dir,
        processed_dir=config.data.processed_dir,
        force=args.force,
    )
    splits = {
        name: load_wic_split(extracted, name)
        for name in (
            config.data.train_split,
            config.data.validation_split,
            config.data.test_split,
        )
    }
    audits = {name: audit_examples(rows, name) for name, rows in splits.items()}
    validate_expected_release(audits.values())
    validate_no_cross_split_pairs(
        splits[config.data.train_split], splits[config.data.validation_split]
    )

    config.data.processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.data.processed_dir / "dataset_audit.json"
    output_path.write_text(
        json.dumps(
            {
                "archive_sha256": config.data.sha256,
                "source_url": config.data.url,
                "splits": {name: audit.to_dict() for name, audit in audits.items()},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({name: audit.to_dict() for name, audit in audits.items()}, indent=2))
    print(f"Audit written to {output_path}")


if __name__ == "__main__":
    main()
