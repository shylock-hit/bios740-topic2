#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_counts(path: Path) -> dict[str, int]:
    dataset = json.loads(path.read_text(encoding="utf-8"))
    samples = [sample for split in dataset.values() for sample in split]
    return {
        "sentences": len(samples),
        "entities": sum(len(sample.get("entities", [])) for sample in samples),
        "relations": sum(len(sample.get("relations", [])) for sample in samples),
        "avg_tokens": round(
            sum(len(sample.get("text", "").split()) for sample in samples) / len(samples), 2
        )
        if samples
        else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate GPU resources for SpERT experiments.")
    parser.add_argument("--adkg", default="data/raw/ADKG.json")
    parser.add_argument("--mdkg", default="data/raw/MDKG.json")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--train-batch-size", type=int, default=2)
    parser.add_argument("--output", default="outputs/resource_estimate.json")
    args = parser.parse_args()

    adkg = load_counts(Path(args.adkg))
    mdkg = load_counts(Path(args.mdkg))
    estimate = {
        "datasets": {"ADKG": adkg, "MDKG": mdkg},
        "training": {
            "epochs": args.epochs,
            "train_batch_size": args.train_batch_size,
            "recommended_vram_gb": {
                "smoke_test": "8-12",
                "single_dataset_full_run": "16-24",
                "four_experiment_suite": "24",
            },
            "wall_clock_hours": {
                "t4_16gb_per_dataset": "2-5",
                "l4_or_a10_per_dataset": "1-3",
                "a100_per_dataset": "<1.5",
            },
            "disk_gb": {
                "data_and_spert_inputs": "<0.1",
                "model_cache": "0.5-0.7",
                "four_experiments_checkpoints": "5-10",
            },
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(estimate, indent=2), encoding="utf-8")
    print(json.dumps(estimate, indent=2))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

