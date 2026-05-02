#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize LLM annotation experiment metrics.")
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--output", default="outputs/llm_runs/summary.md")
    args = parser.parse_args()

    metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    lines = [
        "# LLM Annotation Summary",
        "",
        "## Quality",
        "",
        "| Method | Strict Entity F1 | Strict Relation F1 | Relaxed Entity F1 | Relaxed Relation F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for mode, result in metrics.items():
        lines.append(
            f"| {mode} | "
            f"{result['strict']['entities']['micro']['f1']:.4f} | "
            f"{result['strict']['relations']['micro']['f1']:.4f} | "
            f"{result['relaxed']['entities']['f1']:.4f} | "
            f"{result['relaxed']['relations']['f1']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## System",
            "",
            "| Method | Avg Latency (s) | P50 (s) | P90 (s) | Parse Success | Failures | Validation Errors |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode, result in metrics.items():
        lines.append(
            f"| {mode} | "
            f"{result['avg_latency_seconds']:.4f} | "
            f"{result['p50_latency_seconds']:.4f} | "
            f"{result['p90_latency_seconds']:.4f} | "
            f"{result['parse_success_count']}/{result['parse_success_count'] + result['failure_count']} "
            f"({result['parse_success_rate']:.2%}) | "
            f"{result['failure_count']} | "
            f"{result['validation_error_count']} |"
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
