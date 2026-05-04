from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Protocol

from bios740_topic2.llm_schema import normalize_payload, validate_payload


class LLMClient(Protocol):
    def complete_json(self, prompt_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass
class WorkflowResult:
    mode: str
    payload: dict[str, list[dict[str, str]]]
    errors: list[str]
    latency_seconds: float


def run_one_shot(client: LLMClient, text: str, dataset: str = "ADKG") -> WorkflowResult:
    started = perf_counter()
    payload = normalize_payload(client.complete_json("one_shot", {"text": text, "dataset": dataset}))
    errors = validate_payload(payload, dataset=dataset)
    return WorkflowResult(
        mode="one_shot",
        payload=payload,
        errors=errors,
        latency_seconds=perf_counter() - started,
    )


def run_entities_then_relations(client: LLMClient, text: str, dataset: str = "ADKG") -> WorkflowResult:
    started = perf_counter()
    entities = normalize_payload(client.complete_json("extract_entities", {"text": text, "dataset": dataset}))["entities"]
    relations = normalize_payload(
        client.complete_json("extract_relations", {"text": text, "entities": entities, "dataset": dataset})
    )["relations"]
    reviewed = normalize_payload(
        client.complete_json(
            "review_and_fix",
            {"text": text, "entities": entities, "relations": relations, "dataset": dataset},
        )
    )
    errors = validate_payload(reviewed, dataset=dataset)
    return WorkflowResult(
        mode="workflow",
        payload=reviewed,
        errors=errors,
        latency_seconds=perf_counter() - started,
    )
