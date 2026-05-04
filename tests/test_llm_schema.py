from bios740_topic2.llm_schema import (
    ADKG_ENTITY_TYPES,
    ADKG_RELATION_TYPES,
    MDKG_ENTITY_TYPES,
    MDKG_RELATION_TYPES,
    normalize_payload,
    validate_payload,
    validate_adkg_payload,
)


def test_adkg_schema_contains_expected_labels():
    assert "disease" in ADKG_ENTITY_TYPES
    assert "help_diagnose" in ADKG_RELATION_TYPES


def test_normalize_payload_filters_incomplete_rows():
    payload = {
        "entities": [{"text": "APOE", "type": "gene"}, {"text": "", "type": "gene"}],
        "relations": [{"head": "APOE", "type": "associated_with", "tail": "dementia"}],
    }
    normalized = normalize_payload(payload)
    assert normalized["entities"] == [{"text": "APOE", "type": "gene"}]
    assert normalized["relations"][0]["type"] == "associated_with"


def test_validate_payload_flags_unknown_labels():
    errors = validate_adkg_payload(
        {
            "entities": [{"text": "X", "type": "bad_label"}],
            "relations": [{"head": "X", "type": "bad_rel", "tail": "Y"}],
        }
    )
    assert any("invalid entity type" in error for error in errors)
    assert any("invalid relation type" in error for error in errors)


def test_mdkg_schema_contains_expected_dataset_specific_labels():
    assert "Health_factors" in MDKG_ENTITY_TYPES
    assert "occurs_in" in MDKG_RELATION_TYPES
    assert "treatment_target_for" not in MDKG_RELATION_TYPES


def test_validate_payload_uses_selected_dataset_schema():
    mdkg_payload = {
        "entities": [{"text": "younger age", "type": "Health_factors"}],
        "relations": [{"head": "depression", "type": "occurs_in", "tail": "region"}],
    }
    assert validate_payload(mdkg_payload, dataset="MDKG") == []
    errors = validate_payload(mdkg_payload, dataset="ADKG")
    assert any("invalid entity type" in error for error in errors)
    assert any("invalid relation type" in error for error in errors)
