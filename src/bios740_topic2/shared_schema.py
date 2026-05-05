from __future__ import annotations

from copy import deepcopy
import random
from typing import Any


def shared_schema(types_a: dict[str, Any], types_b: dict[str, Any]) -> dict[str, set[str]]:
    return {
        "entities": set(types_a["entities"]) & set(types_b["entities"]),
        "relations": set(types_a["relations"]) & set(types_b["relations"]),
    }


def filter_sample_to_schema(
    sample: dict[str, Any], entity_types: set[str], relation_types: set[str]
) -> dict[str, Any]:
    kept_entities = []
    old_to_new = {}
    for old_index, entity in enumerate(sample.get("entities", [])):
        if entity["type"] in entity_types:
            old_to_new[old_index] = len(kept_entities)
            kept_entities.append(deepcopy(entity))

    kept_relations = []
    for relation in sample.get("relations", []):
        head = relation["head"]
        tail = relation["tail"]
        if (
            relation["type"] in relation_types
            and head in old_to_new
            and tail in old_to_new
        ):
            kept_relations.append(
                {
                    **deepcopy(relation),
                    "head": old_to_new[head],
                    "tail": old_to_new[tail],
                }
            )

    return {
        **deepcopy(sample),
        "entities": kept_entities,
        "relations": kept_relations,
    }


def filter_dataset_to_schema(
    dataset: dict[str, list[dict[str, Any]]], entity_types: set[str], relation_types: set[str]
) -> dict[str, list[dict[str, Any]]]:
    return {
        split: [filter_sample_to_schema(sample, entity_types, relation_types) for sample in samples]
        for split, samples in dataset.items()
    }


def sample_train_split(
    dataset: dict[str, list[dict[str, Any]]], ratio: float, seed: int = 740
) -> dict[str, list[dict[str, Any]]]:
    if ratio <= 0 or ratio > 1:
        raise ValueError("ratio must be in (0, 1]")
    rng = random.Random(seed)
    train = list(dataset.get("train", []))
    sample_count = max(1, round(len(train) * ratio)) if train else 0
    sampled_train = rng.sample(train, sample_count) if sample_count else []
    return {
        split: deepcopy(samples)
        for split, samples in dataset.items()
        if split != "train"
    } | {"train": sampled_train}


def build_shared_types(entity_types: set[str], relation_types: set[str]) -> dict[str, Any]:
    return {
        "entities": {
            name: {"short": name, "verbose": name}
            for name in sorted(entity_types)
        },
        "relations": {
            name: {"short": name, "verbose": name, "symmetric": False}
            for name in sorted(relation_types)
        },
    }
