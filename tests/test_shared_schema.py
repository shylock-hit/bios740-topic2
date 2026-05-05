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


def test_sample_train_split_is_deterministic_and_preserves_dev_test():
    from bios740_topic2.shared_schema import sample_train_split

    dataset = {
        "train": [{"sent_id": f"s{i}"} for i in range(8)],
        "dev": [{"sent_id": "dev"}],
        "test": [{"sent_id": "test"}],
    }

    sampled_a = sample_train_split(dataset, ratio=0.25, seed=740)
    sampled_b = sample_train_split(dataset, ratio=0.25, seed=740)

    assert len(sampled_a["train"]) == 2
    assert sampled_a["train"] == sampled_b["train"]
    assert sampled_a["dev"] == dataset["dev"]
    assert sampled_a["test"] == dataset["test"]
