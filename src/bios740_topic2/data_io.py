from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_SPLITS = ("train", "dev", "test")


def load_dataset(path: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Load an ADKG/MDKG JSON file and ensure the expected split keys exist."""
    with Path(path).open("r", encoding="utf-8") as handle:
        dataset = json.load(handle)
    missing = [split for split in REQUIRED_SPLITS if split not in dataset]
    if missing:
        raise ValueError(f"Dataset is missing required split(s): {', '.join(missing)}")
    return {split: list(dataset[split]) for split in REQUIRED_SPLITS}


def iter_samples(dataset: dict[str, list[dict[str, Any]]]):
    for split in REQUIRED_SPLITS:
        for sample in dataset.get(split, []):
            yield split, sample


def validate_dataset(dataset: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Return non-fatal validation warnings for offsets and relation endpoints."""
    warnings: list[str] = []
    for split, sample in iter_samples(dataset):
        text = sample.get("text", "")
        sent_id = sample.get("sent_id", "<missing>")
        entity_ids = {entity.get("id") for entity in sample.get("entities", [])}

        for entity in sample.get("entities", []):
            start = entity.get("start")
            end = entity.get("end")
            expected = entity.get("text")
            if not isinstance(start, int) or not isinstance(end, int):
                warnings.append(f"{split}/{sent_id}: invalid offset for {entity.get('id')}")
                continue
            actual = text[start:end]
            if actual != expected:
                warnings.append(
                    f"{split}/{sent_id}: offset mismatch for {entity.get('id')} "
                    f"expected {expected!r}, got {actual!r}"
                )

        for relation in sample.get("relations", []):
            head_id = relation.get("head", {}).get("id")
            tail_id = relation.get("tail", {}).get("id")
            if head_id not in entity_ids:
                warnings.append(f"{split}/{sent_id}: relation has unknown head {head_id!r}")
            if tail_id not in entity_ids:
                warnings.append(f"{split}/{sent_id}: relation has unknown tail {tail_id!r}")
    return warnings

