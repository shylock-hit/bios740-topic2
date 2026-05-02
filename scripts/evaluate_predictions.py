#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.evaluate import boundary_errors, evaluate_dataset


def _load_samples(path: str):
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "test" in payload:
        return payload["test"]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate strict NER/RE predictions.")
    parser.add_argument("--gold", required=True, help="Gold JSON file or dataset JSON with test split")
    parser.add_argument("--pred", required=True, help="Predicted sentence-level JSON file")
    parser.add_argument("--output", default="outputs/evaluation.json", help="Metrics output path")
    args = parser.parse_args()

    gold = _load_samples(args.gold)
    predicted = _load_samples(args.pred)
    result = {
        "metrics": evaluate_dataset(gold, predicted),
        "boundary_errors": boundary_errors(gold, predicted)[:50],
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
