#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.data_io import load_dataset
from bios740_topic2.spert_convert import build_types, convert_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert ADKG/MDKG JSON to SpERT-style JSON files.")
    parser.add_argument("--input", required=True, help="Path to ADKG.json or MDKG.json")
    parser.add_argument("--name", required=True, help="Dataset name, e.g. ADKG or MDKG")
    parser.add_argument("--output-dir", default="outputs/spert", help="Output directory")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    converted = convert_dataset(dataset)
    output_dir = Path(args.output_dir) / args.name.lower()
    output_dir.mkdir(parents=True, exist_ok=True)

    for split, samples in converted.items():
        (output_dir / f"{split}.json").write_text(
            json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    (output_dir / "types.json").write_text(
        json.dumps(build_types(dataset), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote SpERT files to {output_dir}")


if __name__ == "__main__":
    main()
