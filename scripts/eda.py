#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.data_io import load_dataset, validate_dataset
from bios740_topic2.eda import compute_split_stats, compute_type_distributions, relation_distance_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EDA for ADKG/MDKG JSON datasets.")
    parser.add_argument("--input", required=True, help="Path to ADKG.json or MDKG.json")
    parser.add_argument("--name", required=True, help="Dataset name, e.g. ADKG or MDKG")
    parser.add_argument("--output-dir", default="outputs", help="Directory for EDA artifacts")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "dataset": args.name,
        "validation_warnings": validate_dataset(dataset),
        "split_stats": compute_split_stats(dataset),
        "type_distributions": compute_type_distributions(dataset),
        "relation_distance": relation_distance_summary(dataset),
    }
    output_path = output_dir / f"{args.name.lower()}_eda_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
