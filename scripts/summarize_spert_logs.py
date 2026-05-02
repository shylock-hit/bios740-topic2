#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MICRO_RE = re.compile(r"^\s+micro\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s*$")


def parse_log(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = text.split("Evaluation")
    if len(blocks) < 2:
        return {"log": str(path), "error": "No Evaluation block found"}

    block = blocks[-1]
    entity_micro = None
    rel_without_nec = None
    rel_with_nec = None
    section = None

    for line in block.splitlines():
        if "--- Entities" in line:
            section = "entities"
        elif "Without named entity classification" in line:
            section = "relations_without_nec"
        elif "With named entity classification" in line:
            section = "relations_with_nec"
        match = MICRO_RE.match(line)
        if match:
            metric = {
                "precision": float(match.group(1)),
                "recall": float(match.group(2)),
                "f1": float(match.group(3)),
                "support": int(match.group(4)),
            }
            if section == "entities":
                entity_micro = metric
            elif section == "relations_without_nec":
                rel_without_nec = metric
            elif section == "relations_with_nec":
                rel_with_nec = metric

    saved = re.findall(r"Saved in:\s*(.+)", text)
    logged = re.findall(r"Logged in:\s*(.+)", text)
    return {
        "log": str(path),
        "entity_micro": entity_micro,
        "relation_without_nec_micro": rel_without_nec,
        "relation_with_nec_micro": rel_with_nec,
        "saved_in": saved[-1] if saved else None,
        "logged_in": logged[-1] if logged else None,
    }


def row(name: str, result: dict[str, object]) -> str:
    ent = result.get("entity_micro") or {}
    rel = result.get("relation_with_nec_micro") or {}
    return (
        f"| {name} | {ent.get('precision', 'TBD')} | {ent.get('recall', 'TBD')} | "
        f"{ent.get('f1', 'TBD')} | {rel.get('precision', 'TBD')} | "
        f"{rel.get('recall', 'TBD')} | {rel.get('f1', 'TBD')} |"
    )


def write_markdown(results: dict[str, dict[str, object]], output: Path) -> None:
    lines = [
        "# SpERT Metrics Summary",
        "",
        "## Main Results",
        "",
        "| Run | Entity P | Entity R | Entity F1 | Relation P (NEC) | Relation R (NEC) | Relation F1 (NEC) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, result in results.items():
        lines.append(row(name, result))
    lines.extend(["", "## Checkpoints", "", "| Run | Saved In | Log Dir |", "| --- | --- | --- |"])
    for name, result in results.items():
        lines.append(f"| {name} | {result.get('saved_in')} | {result.get('logged_in')} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize final SpERT console logs.")
    parser.add_argument("--adkg-log", default="outputs/logs/adkg_train_console.log")
    parser.add_argument("--mdkg-log", default="outputs/logs/mdkg_train_console.log")
    parser.add_argument("--output-dir", default="outputs/final_summary")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, log_path in {"ADKG": Path(args.adkg_log), "MDKG": Path(args.mdkg_log)}.items():
        if log_path.exists():
            results[name] = parse_log(log_path)
        else:
            results[name] = {"log": str(log_path), "error": "missing log"}

    (output_dir / "metrics_summary.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    write_markdown(results, output_dir / "metrics_summary.md")
    print(f"Wrote {output_dir / 'metrics_summary.json'}")
    print(f"Wrote {output_dir / 'metrics_summary.md'}")


if __name__ == "__main__":
    main()

