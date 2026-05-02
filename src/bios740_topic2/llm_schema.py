from __future__ import annotations

from typing import Any


ADKG_ENTITY_TYPES = (
    "disease",
    "gene",
    "drug",
    "method",
    "mutation",
    "other",
)

ADKG_RELATION_TYPES = (
    "abbreviation_for",
    "associated_with",
    "characteristic_of",
    "help_diagnose",
    "hyponym_of",
    "risk_factor_of",
    "treatment_for",
    "treatment_target_for",
)


def normalize_payload(payload: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    entities = payload.get("entities") or []
    relations = payload.get("relations") or []
    return {
        "entities": [
            {"text": str(entity["text"]).strip(), "type": str(entity["type"]).strip()}
            for entity in entities
            if entity.get("text") and entity.get("type")
        ],
        "relations": [
            {
                "head": str(relation["head"]).strip(),
                "type": str(relation["type"]).strip(),
                "tail": str(relation["tail"]).strip(),
            }
            for relation in relations
            if relation.get("head") and relation.get("type") and relation.get("tail")
        ],
    }


def validate_adkg_payload(payload: dict[str, Any]) -> list[str]:
    normalized = normalize_payload(payload)
    errors: list[str] = []
    for entity in normalized["entities"]:
        if entity["type"] not in ADKG_ENTITY_TYPES:
            errors.append(f"invalid entity type: {entity['type']}")
    for relation in normalized["relations"]:
        if relation["type"] not in ADKG_RELATION_TYPES:
            errors.append(f"invalid relation type: {relation['type']}")
    return errors
