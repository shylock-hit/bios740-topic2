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

MDKG_ENTITY_TYPES = (
    "disease",
    "method",
    "Health_factors",
    "drug",
    "gene",
    "physiology",
    "region",
    "signs",
    "symptom",
)

MDKG_RELATION_TYPES = (
    "abbreviation_for",
    "associated_with",
    "characteristic_of",
    "help_diagnose",
    "hyponym_of",
    "located_in",
    "occurs_in",
    "risk_factor_of",
    "treatment_for",
)

DATASET_SCHEMAS = {
    "ADKG": {"entities": ADKG_ENTITY_TYPES, "relations": ADKG_RELATION_TYPES},
    "MDKG": {"entities": MDKG_ENTITY_TYPES, "relations": MDKG_RELATION_TYPES},
}


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
    return validate_payload(payload, dataset="ADKG")


def validate_payload(payload: dict[str, Any], dataset: str = "ADKG") -> list[str]:
    dataset_key = dataset.upper()
    if dataset_key not in DATASET_SCHEMAS:
        raise ValueError(f"Unsupported dataset: {dataset}")
    schema = DATASET_SCHEMAS[dataset_key]
    normalized = normalize_payload(payload)
    errors: list[str] = []
    for entity in normalized["entities"]:
        if entity["type"] not in schema["entities"]:
            errors.append(f"invalid entity type: {entity['type']}")
    for relation in normalized["relations"]:
        if relation["type"] not in schema["relations"]:
            errors.append(f"invalid relation type: {relation['type']}")
    return errors
