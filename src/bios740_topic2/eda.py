from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from .data_io import REQUIRED_SPLITS


def compute_split_stats(dataset: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for split in REQUIRED_SPLITS:
        samples = dataset.get(split, [])
        sentence_count = len(samples)
        entity_count = sum(len(sample.get("entities", [])) for sample in samples)
        relation_count = sum(len(sample.get("relations", [])) for sample in samples)
        token_lengths = [len(sample.get("text", "").split()) for sample in samples]
        stats[split] = {
            "sentences": sentence_count,
            "entities": entity_count,
            "relations": relation_count,
            "entities_per_sentence": round(entity_count / sentence_count, 4)
            if sentence_count
            else 0.0,
            "relations_per_sentence": round(relation_count / sentence_count, 4)
            if sentence_count
            else 0.0,
            "avg_tokens": round(mean(token_lengths), 4) if token_lengths else 0.0,
        }
    return stats


def compute_type_distributions(dataset: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, int]]:
    entity_types: Counter[str] = Counter()
    relation_types: Counter[str] = Counter()
    relation_pairs: Counter[str] = Counter()

    for samples in dataset.values():
        for sample in samples:
            id_to_type = {entity["id"]: entity["type"] for entity in sample.get("entities", [])}
            for entity in sample.get("entities", []):
                entity_types[entity["type"]] += 1
            for relation in sample.get("relations", []):
                rel_type = relation["type"]
                relation_types[rel_type] += 1
                head_type = relation.get("head", {}).get("type") or id_to_type.get(
                    relation.get("head", {}).get("id"), "UNK"
                )
                tail_type = relation.get("tail", {}).get("type") or id_to_type.get(
                    relation.get("tail", {}).get("id"), "UNK"
                )
                relation_pairs[f"{head_type}->{tail_type}:{rel_type}"] += 1

    return {
        "entity_types": dict(sorted(entity_types.items())),
        "relation_types": dict(sorted(relation_types.items())),
        "relation_pairs": dict(sorted(relation_pairs.items())),
    }


def relation_distance_summary(dataset: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
    distances: list[int] = []
    for samples in dataset.values():
        for sample in samples:
            entity_index = {entity["id"]: entity for entity in sample.get("entities", [])}
            for relation in sample.get("relations", []):
                head = entity_index.get(relation.get("head", {}).get("id"))
                tail = entity_index.get(relation.get("tail", {}).get("id"))
                if head and tail:
                    distances.append(abs(head["start"] - tail["start"]))
    if not distances:
        return {"count": 0, "avg_char_distance": 0.0, "max_char_distance": 0}
    return {
        "count": len(distances),
        "avg_char_distance": round(mean(distances), 4),
        "max_char_distance": max(distances),
    }

