from fixtures import sample_dataset


def test_relaxed_entity_match_accepts_overlap():
    from bios740_topic2.relaxed_evaluate import relaxed_entity_metrics

    gold = sample_dataset()["train"]
    predicted = [
        {
            **gold[0],
            "entities": [
                {**gold[0]["entities"][0], "end": 7, "text": "18F-FDG"},
                gold[0]["entities"][1],
            ],
            "relations": [],
        }
    ]
    metrics = relaxed_entity_metrics(gold, predicted)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0


def test_relaxed_relation_match_accepts_endpoint_overlap():
    from bios740_topic2.relaxed_evaluate import relaxed_relation_metrics

    gold = sample_dataset()["train"]
    predicted = [
        {
            **gold[0],
            "entities": [
                {**gold[0]["entities"][0], "end": 7, "text": "18F-FDG"},
                gold[0]["entities"][1],
            ],
            "relations": [
                {
                    "type": "help_diagnose",
                    "head": {**gold[0]["entities"][0], "end": 7, "text": "18F-FDG"},
                    "tail": gold[0]["entities"][1],
                }
            ],
        }
    ]
    metrics = relaxed_relation_metrics(gold, predicted)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
