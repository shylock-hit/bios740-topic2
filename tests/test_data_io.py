import json

from fixtures import sample_dataset


def test_load_dataset_reads_required_splits(tmp_path):
    from bios740_topic2.data_io import load_dataset

    path = tmp_path / "ADKG.json"
    path.write_text(json.dumps(sample_dataset()), encoding="utf-8")

    dataset = load_dataset(path)

    assert set(dataset) == {"train", "dev", "test"}
    assert dataset["train"][0]["sent_id"] == "1_s0"


def test_validate_dataset_reports_offset_and_relation_errors():
    from bios740_topic2.data_io import validate_dataset

    dataset = sample_dataset()
    dataset["train"][0]["entities"][0]["text"] = "wrong"
    dataset["train"][0]["relations"][0]["tail"]["id"] = "missing"

    warnings = validate_dataset(dataset)

    assert any("offset mismatch" in warning for warning in warnings)
    assert any("unknown tail" in warning for warning in warnings)

