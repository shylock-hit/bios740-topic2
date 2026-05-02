#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.data_io import load_dataset


def infer_dataset_name(path: str) -> str:
    stem = Path(path).stem.strip()
    return stem.upper() if stem else "UNKNOWN"


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample dev sentences for LLM annotation.")
    parser.add_argument("--input", default="data/raw/ADKG.json")
    parser.add_argument("--output", default="outputs/llm_runs/adkg_dev_sample.json")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=740)
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    dev = list(dataset["dev"])
    if not dev:
        raise ValueError(f"No dev samples found in {args.input}")
    rng = random.Random(args.seed)
    sample_count = min(args.count, len(dev))
    sampled = rng.sample(dev, sample_count)

    output = {
        "dataset": infer_dataset_name(args.input),
        "split": "dev",
        "seed": args.seed,
        "count": sample_count,
        "samples": sampled,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
