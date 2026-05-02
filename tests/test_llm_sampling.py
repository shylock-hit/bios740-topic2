import json
import subprocess
import sys
from pathlib import Path


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


def test_sample_script_infers_dataset_name_from_input_path(tmp_path):
    from bios740_topic2.data_io import load_dataset

    path = tmp_path / "MDKG.json"
    dataset = {
        "train": [],
        "dev": [{"sent_id": "s1", "text": "x", "entities": [], "relations": []}],
        "test": [],
    }
    path.write_text(json.dumps(dataset), encoding="utf-8")
    loaded = load_dataset(path)

    dataset_name = path.stem.upper()
    output = {
        "dataset": dataset_name,
        "split": "dev",
        "seed": 740,
        "count": 1,
        "samples": list(loaded["dev"]),
    }

    assert output["dataset"] == "MDKG"


def test_legacy_adkg_sample_script_still_works(tmp_path):
    path = tmp_path / "ADKG.json"
    dataset = {
        "train": [],
        "dev": [{"sent_id": "s1", "text": "x", "entities": [], "relations": []}],
        "test": [],
    }
    path.write_text(json.dumps(dataset), encoding="utf-8")
    output = tmp_path / "sample.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/sample_adkg_dev_for_llm.py",
            "--input",
            str(path),
            "--output",
            str(output),
            "--count",
            "1",
            "--seed",
            "740",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["dataset"] == "ADKG"
    assert payload["count"] == 1
