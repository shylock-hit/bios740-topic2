import json


def test_sampling_is_deterministic(tmp_path):
    from bios740_topic2.data_io import load_dataset

    path = tmp_path / "ADKG.json"
    dataset = {
        "train": [],
        "dev": [{"sent_id": f"s{i}", "text": str(i), "entities": [], "relations": []} for i in range(10)],
        "test": [],
    }
    path.write_text(json.dumps(dataset), encoding="utf-8")
    loaded = load_dataset(path)

    import random

    rng1 = random.Random(740)
    rng2 = random.Random(740)
    sample1 = rng1.sample(list(loaded["dev"]), 3)
    sample2 = rng2.sample(list(loaded["dev"]), 3)
    assert [item["sent_id"] for item in sample1] == [item["sent_id"] for item in sample2]
