#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


MICRO_RE = re.compile(r"^\s+micro\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s*$")


RUNS = [
    {
        "run": "MDKG 25% baseline",
        "target": "MDKG",
        "setting": "PubMedBERT -> MDKG_shared train_25",
        "dev_log": "outputs/logs/mdkg25_baseline_dev_eval.log",
        "test_log": "outputs/logs/mdkg25_baseline_test_eval.log",
    },
    {
        "run": "ADKG -> MDKG 25% transfer",
        "target": "MDKG",
        "setting": "ADKG_shared full source -> MDKG_shared train_25",
        "dev_log": "outputs/logs/adkg_to_mdkg25_transfer_dev_eval.log",
        "test_log": "outputs/logs/adkg_to_mdkg25_transfer_test_eval.log",
    },
    {
        "run": "ADKG 25% baseline",
        "target": "ADKG",
        "setting": "PubMedBERT -> ADKG_shared train_25",
        "dev_log": "outputs/logs/adkg25_baseline_dev_eval.log",
        "test_log": "outputs/logs/adkg25_baseline_test_eval.log",
    },
    {
        "run": "MDKG -> ADKG 25% transfer",
        "target": "ADKG",
        "setting": "MDKG_shared full source -> ADKG_shared train_25",
        "dev_log": "outputs/logs/mdkg_to_adkg25_transfer_dev_eval.log",
        "test_log": "outputs/logs/mdkg_to_adkg25_transfer_test_eval.log",
    },
]


def parse_eval_log(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"log": str(path), "error": "missing log"}

    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = text.split("Evaluation")
    if len(blocks) < 2:
        return {"log": str(path), "error": "No Evaluation block found"}

    block = blocks[-1]
    section = None
    entity_micro = None
    rel_with_nec = None

    for line in block.splitlines():
        if "--- Entities" in line:
            section = "entities"
        elif "With named entity classification" in line:
            section = "relations_with_nec"
        elif "Without named entity classification" in line:
            section = "relations_without_nec"

        match = MICRO_RE.match(line)
        if not match:
            continue
        metric = {
            "precision": float(match.group(1)),
            "recall": float(match.group(2)),
            "f1": float(match.group(3)),
            "support": int(match.group(4)),
        }
        if section == "entities":
            entity_micro = metric
        elif section == "relations_with_nec":
            rel_with_nec = metric

    return {
        "log": str(path),
        "entity_micro": entity_micro,
        "relation_with_nec_micro": rel_with_nec,
    }


def _f1(result: dict[str, Any], key: str) -> Any:
    metric = result.get(key) or {}
    return metric.get("f1", "TBD")


def _delta(transfer: Any, baseline: Any) -> Any:
    if isinstance(transfer, (int, float)) and isinstance(baseline, (int, float)):
        return round(transfer - baseline, 2)
    return "TBD"


def build_summary() -> dict[str, Any]:
    rows = []
    for run in RUNS:
        dev = parse_eval_log(Path(run["dev_log"]))
        test = parse_eval_log(Path(run["test_log"]))
        rows.append(
            {
                **run,
                "dev": dev,
                "test": test,
                "dev_entity_f1": _f1(dev, "entity_micro"),
                "dev_relation_nec_f1": _f1(dev, "relation_with_nec_micro"),
                "test_entity_f1": _f1(test, "entity_micro"),
                "test_relation_nec_f1": _f1(test, "relation_with_nec_micro"),
            }
        )

    by_run = {row["run"]: row for row in rows}
    comparisons = [
        {
            "target": "MDKG",
            "baseline": "MDKG 25% baseline",
            "transfer": "ADKG -> MDKG 25% transfer",
        },
        {
            "target": "ADKG",
            "baseline": "ADKG 25% baseline",
            "transfer": "MDKG -> ADKG 25% transfer",
        },
    ]
    for comparison in comparisons:
        baseline = by_run[comparison["baseline"]]
        transfer = by_run[comparison["transfer"]]
        comparison["dev_relation_nec_f1_delta"] = _delta(
            transfer["dev_relation_nec_f1"], baseline["dev_relation_nec_f1"]
        )
        comparison["test_relation_nec_f1_delta"] = _delta(
            transfer["test_relation_nec_f1"], baseline["test_relation_nec_f1"]
        )
        comparison["dev_entity_f1_delta"] = _delta(
            transfer["dev_entity_f1"], baseline["dev_entity_f1"]
        )
        comparison["test_entity_f1_delta"] = _delta(
            transfer["test_entity_f1"], baseline["test_entity_f1"]
        )

    return {"runs": rows, "comparisons": comparisons}


def write_markdown(summary: dict[str, Any], output: Path) -> None:
    lines = [
        "# Extension B Low-Resource Shared-Schema Transfer Summary",
        "",
        "Target train ratio: 25%. Shared entity types: disease, drug, gene, method. Shared relation types: abbreviation_for, associated_with, characteristic_of, help_diagnose, hyponym_of, risk_factor_of, treatment_for.",
        "",
        "## Main Results",
        "",
        "| Run | Target | Setting | Dev Ent F1 | Dev Rel F1 (NEC) | Test Ent F1 | Test Rel F1 (NEC) |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["runs"]:
        lines.append(
            f"| {row['run']} | {row['target']} | {row['setting']} | "
            f"{row['dev_entity_f1']} | {row['dev_relation_nec_f1']} | "
            f"{row['test_entity_f1']} | {row['test_relation_nec_f1']} |"
        )
    lines.extend(
        [
            "",
            "## Transfer Deltas",
            "",
            "| Target | Transfer vs Baseline | Dev Rel F1 Delta | Test Rel F1 Delta | Dev Ent F1 Delta | Test Ent F1 Delta |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for comparison in summary["comparisons"]:
        lines.append(
            f"| {comparison['target']} | {comparison['transfer']} vs {comparison['baseline']} | "
            f"{comparison['dev_relation_nec_f1_delta']} | {comparison['test_relation_nec_f1_delta']} | "
            f"{comparison['dev_entity_f1_delta']} | {comparison['test_entity_f1_delta']} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Extension B low-resource transfer eval logs.")
    parser.add_argument("--output-dir", default="outputs/final_summary")
    parser.add_argument("--runs-json", default="outputs/final_summary/extension_b_low_resource_runs.json")
    args = parser.parse_args()

    summary = build_summary()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = Path(args.runs_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md_path = output_dir / "extension_b_low_resource_transfer_summary.md"
    write_markdown(summary, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
