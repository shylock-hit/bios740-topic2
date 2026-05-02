#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.experiments import write_configs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SpERT config templates.")
    parser.add_argument("--output-dir", default="outputs/spert_configs")
    args = parser.parse_args()

    for path in write_configs(args.output_dir):
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
