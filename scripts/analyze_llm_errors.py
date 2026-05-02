#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.evaluate import boundary_errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze common error patterns in LLM predictions.")
    parser.add_argument("--gold", required=True, help="Gold samples JSON list")
    parser.add_argument("--pred", required=True, help="Predicted samples JSON list")
    parser.add_argument("--progress-jsonl", help="Optional progress log to summarize failed API calls")
    parser.add_argument("--output", default="outputs/llm_runs/error_summary.md")
    args = parser.parse_args()

    gold_payload = json.loads(Path(args.gold).read_text(encoding="utf-8"))
    pred = json.loads(Path(args.pred).read_text(encoding="utf-8"))
    gold = gold_payload["samples"] if isinstance(gold_payload, dict) and "samples" in gold_payload else gold_payload
    boundary = boundary_errors(gold, pred)

    failure_counter = Counter()
    if args.progress_jsonl and Path(args.progress_jsonl).exists():
        for line in Path(args.progress_jsonl).read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("status") == "failed" and record.get("failure"):
                failure_counter[record["failure"]["error_type"]] += 1

    lines = [
        "# LLM Error Summary",
        "",
        f"- Boundary overlap errors: {len(boundary)}",
    ]
    if failure_counter:
        lines.append(f"- API/runtime failures: {sum(failure_counter.values())}")
        lines.append("")
        lines.append("## Failure Types")
        lines.append("")
        for error_type, count in failure_counter.most_common():
            lines.append(f"- `{error_type}`: {count}")
    if boundary:
        lines.append("")
        lines.append("## Boundary Error Examples")
        lines.append("")
        for example in boundary[:10]:
            lines.append(
                f"- `{example['sent_id']}` {example['type']}: gold `{example['gold_text']}` vs pred `{example['pred_text']}`"
            )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
