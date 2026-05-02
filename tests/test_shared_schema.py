def test_filter_dataset_to_shared_schema_remaps_relations():
    from bios740_topic2.shared_schema import filter_dataset_to_schema

    dataset = {
        "train": [
            {
                "tokens": ["A", "B", "C"],
                "entities": [
                    {"type": "drug", "start": 0, "end": 1},
                    {"type": "other", "start": 1, "end": 2},
                    {"type": "disease", "start": 2, "end": 3},
                ],
                "relations": [
                    {"type": "treatment_for", "head": 0, "tail": 2},
                    {"type": "associated_with", "head": 1, "tail": 2},
                ],
            }
        ],
        "dev": [],
        "test": [],
    }

    filtered = filter_dataset_to_schema(
        dataset,
        entity_types={"drug", "disease"},
        relation_types={"treatment_for", "associated_with"},
    )

    sample = filtered["train"][0]
    assert [entity["type"] for entity in sample["entities"]] == ["drug", "disease"]
    assert sample["relations"] == [{"type": "treatment_for", "head": 0, "tail": 1}]
