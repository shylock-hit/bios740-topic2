#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.brat_convert import convert_brat_directory
from bios740_topic2.data_io import validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert ADERC/MDIEC brat sources to course JSON.")
    parser.add_argument("--adkg-source", default="data/raw_sources/ADERC/all_dec")
    parser.add_argument("--mdkg-source", default="data/raw_sources/MDIEC/MDIEC")
    parser.add_argument("--output-dir", default="data/raw")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, source in [("ADKG", args.adkg_source), ("MDKG", args.mdkg_source)]:
        dataset = convert_brat_directory(source)
        warnings = validate_dataset(dataset)
        output = output_dir / f"{name}.json"
        output.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
        split_counts = {split: len(samples) for split, samples in dataset.items()}
        print(f"Wrote {output} with splits {split_counts}; validation warnings={len(warnings)}")


if __name__ == "__main__":
    main()

