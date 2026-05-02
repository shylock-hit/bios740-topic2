#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.evaluate import evaluate_dataset
from bios740_topic2.llm_client import OpenAICompatConfig, OpenAICompatibleClient
from bios740_topic2.llm_postprocess import build_prediction_sample
from bios740_topic2.llm_workflow import run_entities_then_relations, run_one_shot
from bios740_topic2.relaxed_evaluate import relaxed_entity_metrics, relaxed_relation_metrics


class MockLLMClient:
    def complete_json(self, prompt_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        text = payload["text"]
        if prompt_name == "one_shot":
            return _heuristic_extract(text)
        if prompt_name == "extract_entities":
            return {"entities": _heuristic_extract(text)["entities"], "relations": []}
        if prompt_name == "extract_relations":
            return {"entities": [], "relations": _heuristic_extract(text)["relations"]}
        if prompt_name == "review_and_fix":
            return {"entities": payload.get("entities", []), "relations": payload.get("relations", [])}
        raise ValueError(f"Unknown prompt {prompt_name}")


def _heuristic_extract(text: str) -> dict[str, list[dict[str, str]]]:
    payload = {"entities": [], "relations": []}
    if "PET" in text:
        payload["entities"].append({"text": "18F-FDG PET", "type": "method"})
    if "dementia" in text:
        payload["entities"].append({"text": "focal dementia", "type": "disease"})
    if "helps diagnose" in text and len(payload["entities"]) >= 2:
        payload["relations"].append(
            {"head": "18F-FDG PET", "type": "help_diagnose", "tail": "focal dementia"}
        )
    return payload


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percentile
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    weight = rank - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LLM annotation experiment on sampled ADKG data.")
    parser.add_argument("--sample", required=True, help="Sample JSON produced by sample_adkg_dev_for_llm.py")
    parser.add_argument("--output-dir", default="outputs/llm_runs/mock_run")
    parser.add_argument("--mode", choices=("one_shot", "workflow", "both"), default="both")
    parser.add_argument("--provider", choices=("mock", "openai_compat"), default="mock")
    parser.add_argument("--env-file", default=".env.llm")
    args = parser.parse_args()

    sample_payload = json.loads(Path(args.sample).read_text(encoding="utf-8"))
    gold_samples = sample_payload["samples"]
    if not gold_samples:
        raise ValueError(f"No samples found in {args.sample}")
    client = (
        MockLLMClient()
        if args.provider == "mock"
        else OpenAICompatibleClient(OpenAICompatConfig.from_env(args.env_file))
    )

    modes = ["one_shot", "workflow"] if args.mode == "both" else [args.mode]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {}

    for mode in modes:
        predictions = []
        latencies = []
        errors = 0
        parse_success = 0
        failures = 0
        progress_json = output_dir / f"{mode}_progress.json"
        progress_jsonl = output_dir / f"{mode}_progress.jsonl"
        if progress_jsonl.exists():
            progress_jsonl.unlink()

        for index, sample in enumerate(gold_samples, start=1):
            try:
                result = run_one_shot(client, sample["text"]) if mode == "one_shot" else run_entities_then_relations(client, sample["text"])
                prediction = build_prediction_sample(sample, result.payload)
                predictions.append(prediction)
                latencies.append(result.latency_seconds)
                errors += len(result.errors)
                parse_success += 1
                failure_payload = None
            except Exception as exc:
                predictions.append(
                    {
                        "doc_id": sample.get("doc_id"),
                        "sent_id": sample["sent_id"],
                        "text": sample["text"],
                        "entities": [],
                        "relations": [],
                    }
                )
                failures += 1
                failure_payload = {"error_type": type(exc).__name__, "error": str(exc)}

            _write_json(
                progress_json,
                {
                    "mode": mode,
                    "processed": index,
                    "total": len(gold_samples),
                    "avg_latency_seconds": sum(latencies) / len(latencies) if latencies else 0.0,
                    "validation_error_count": errors,
                    "parse_success_count": parse_success,
                    "failure_count": failures,
                    "last_sent_id": sample["sent_id"],
                },
            )
            _append_jsonl(
                progress_jsonl,
                {
                    "index": index,
                    "sent_id": sample["sent_id"],
                    "latency_seconds": latencies[-1] if latencies else 0.0,
                    "validation_error_count": len(result.errors) if failure_payload is None else 0,
                    "status": "ok" if failure_payload is None else "failed",
                    "failure": failure_payload,
                },
            )
            _write_json(output_dir / f"{mode}_predictions.json", predictions)
            if index % 5 == 0 or index == len(gold_samples):
                print(f"[{mode}] processed {index}/{len(gold_samples)}")

        strict_metrics = evaluate_dataset(gold_samples, predictions)
        relaxed_metrics = {
            "entities": relaxed_entity_metrics(gold_samples, predictions),
            "relations": relaxed_relation_metrics(gold_samples, predictions),
        }
        mode_result = {
            "strict": strict_metrics,
            "relaxed": relaxed_metrics,
            "avg_latency_seconds": sum(latencies) / len(latencies) if latencies else 0.0,
            "p50_latency_seconds": _percentile(latencies, 0.50),
            "p90_latency_seconds": _percentile(latencies, 0.90),
            "parse_success_count": parse_success,
            "parse_success_rate": parse_success / len(gold_samples) if gold_samples else 0.0,
            "failure_count": failures,
            "validation_error_count": errors,
        }
        summary[mode] = mode_result
        _write_json(output_dir / f"{mode}_predictions.json", predictions)

    _write_json(output_dir / "metrics.json", summary)
    print(f"Wrote {output_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
