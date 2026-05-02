from __future__ import annotations

import re
from typing import Any


def tokenize_with_offsets(text: str) -> list[tuple[str, int, int]]:
    return [(match.group(0), match.start(), match.end()) for match in re.finditer(r"\S+", text)]


def char_span_to_token_span(
    token_offsets: list[tuple[str, int, int]], start: int, end: int
) -> tuple[int, int]:
    covered = [
        index
        for index, (_, token_start, token_end) in enumerate(token_offsets)
        if token_start < end and token_end > start
    ]
    if not covered:
        raise ValueError(f"Could not align character span {start}:{end} to tokens")
    return covered[0], covered[-1] + 1


def convert_sample(sample: dict[str, Any]) -> dict[str, Any]:
    token_offsets = tokenize_with_offsets(sample["text"])
    tokens = [token for token, _, _ in token_offsets]
    entities = []
    entity_id_to_index = {}

    for index, entity in enumerate(sample.get("entities", [])):
        token_start, token_end = char_span_to_token_span(
            token_offsets, entity["start"], entity["end"]
        )
        entity_id_to_index[entity["id"]] = index
        entities.append(
            {
                "type": entity["type"],
                "start": token_start,
                "end": token_end,
                "id": entity["id"],
                "text": entity["text"],
            }
        )

    relations = []
    for relation in sample.get("relations", []):
        head_id = relation["head"]["id"]
        tail_id = relation["tail"]["id"]
        if head_id not in entity_id_to_index or tail_id not in entity_id_to_index:
            continue
        relations.append(
            {
                "type": relation["type"],
                "head": entity_id_to_index[head_id],
                "tail": entity_id_to_index[tail_id],
            }
        )

    return {
        "orig_id": sample.get("sent_id"),
        "tokens": tokens,
        "entities": entities,
        "relations": relations,
    }


def convert_dataset(dataset: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    return {split: [convert_sample(sample) for sample in samples] for split, samples in dataset.items()}


def build_types(dataset: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, dict[str, str]]]:
    entity_types = sorted(
        {entity["type"] for samples in dataset.values() for sample in samples for entity in sample.get("entities", [])}
    )
    relation_types = sorted(
        {
            relation["type"]
            for samples in dataset.values()
            for sample in samples
            for relation in sample.get("relations", [])
        }
    )
    return {
        "entities": {name: {"short": name, "verbose": name} for name in entity_types},
        "relations": {name: {"short": name, "verbose": name, "symmetric": False} for name in relation_types},
    }

