#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import pandas as pd


def _write_bar(df: pd.DataFrame, x: str, ys: list[str], title: str, ylabel: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    df.plot(x=x, y=ys, kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _write_latency_plot(df: pd.DataFrame, title: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df["index"], df["latency_seconds"], color="#4C78A8")
    ax.set_title(title)
    ax.set_xlabel("Processed sample index")
    ax.set_ylabel("Latency (s)")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate charts for LLM annotation experiments.")
    parser.add_argument("--run-dir", required=True, help="Experiment directory containing metrics and progress files.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    output_dir = run_dir / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    quality_rows = []
    system_rows = []
    for mode, result in metrics.items():
        quality_rows.append(
            {
                "method": mode,
                "strict_entity_f1": result["strict"]["entities"]["micro"]["f1"],
                "strict_relation_f1": result["strict"]["relations"]["micro"]["f1"],
                "relaxed_entity_f1": result["relaxed"]["entities"]["f1"],
                "relaxed_relation_f1": result["relaxed"]["relations"]["f1"],
            }
        )
        system_rows.append(
            {
                "method": mode,
                "avg_latency_seconds": result["avg_latency_seconds"],
                "p50_latency_seconds": result["p50_latency_seconds"],
                "p90_latency_seconds": result["p90_latency_seconds"],
                "parse_success_rate": result["parse_success_rate"],
                "validation_error_count": result["validation_error_count"],
                "failure_count": result["failure_count"],
            }
        )

    quality_df = pd.DataFrame(quality_rows)
    system_df = pd.DataFrame(system_rows)
    quality_df.to_csv(output_dir / "quality_metrics.csv", index=False)
    system_df.to_csv(output_dir / "system_metrics.csv", index=False)

    _write_bar(
        quality_df,
        "method",
        ["strict_entity_f1", "strict_relation_f1", "relaxed_entity_f1", "relaxed_relation_f1"],
        "LLM Annotation Quality Comparison",
        "F1",
        output_dir / "quality_comparison.png",
    )
    _write_bar(
        system_df,
        "method",
        ["avg_latency_seconds", "p50_latency_seconds", "p90_latency_seconds"],
        "Latency Comparison",
        "Seconds",
        output_dir / "latency_comparison.png",
    )
    _write_bar(
        system_df,
        "method",
        ["parse_success_rate", "validation_error_count", "failure_count"],
        "Stability Comparison",
        "Value",
        output_dir / "stability_comparison.png",
    )

    index_lines = ["# LLM Artifact Index", ""]
    for mode in ("one_shot", "workflow"):
        progress_path = run_dir / f"{mode}_progress.jsonl"
        if not progress_path.exists():
            continue
        progress_rows = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        progress_df = pd.DataFrame(progress_rows)
        if "latency_seconds" in progress_df.columns and not progress_df.empty:
            progress_df.to_csv(output_dir / f"{mode}_progress.csv", index=False)
            _write_latency_plot(
                progress_df,
                f"{mode} Per-sample Latency",
                output_dir / f"{mode}_latency_trace.png",
            )
        index_lines.append(f"- `{mode}_latency_trace.png`")
    index_lines.extend(
        [
            "- `quality_comparison.png`",
            "- `latency_comparison.png`",
            "- `stability_comparison.png`",
        ]
    )
    (output_dir / "artifact_index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Wrote LLM artifacts to {output_dir}")


if __name__ == "__main__":
    main()
