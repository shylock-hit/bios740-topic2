from fixtures import sample_dataset


def test_strict_metrics_return_micro_scores_for_exact_matches():
    from bios740_topic2.evaluate import evaluate_dataset

    gold = sample_dataset()["train"]
    predicted = sample_dataset()["train"]

    metrics = evaluate_dataset(gold, predicted)

    assert metrics["entities"]["micro"]["precision"] == 1.0
    assert metrics["entities"]["micro"]["recall"] == 1.0
    assert metrics["entities"]["micro"]["f1"] == 1.0
    assert metrics["relations"]["micro"]["f1"] == 1.0


def test_boundary_error_detection_finds_one_word_miss():
    from bios740_topic2.evaluate import boundary_errors

    gold = sample_dataset()["train"]
    predicted = sample_dataset()["train"].copy()
    predicted = [
        {
            **predicted[0],
            "entities": [
                {**predicted[0]["entities"][0], "end": 7, "text": "18F-FDG"},
                predicted[0]["entities"][1],
            ],
        }
    ]

    errors = boundary_errors(gold, predicted)

    assert len(errors) == 1
    assert errors[0]["gold_text"] == "18F-FDG PET"
