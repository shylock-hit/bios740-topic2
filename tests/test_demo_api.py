import json
from pathlib import Path

from fastapi.testclient import TestClient

from bios740_topic2 import demo_api


def test_sample_endpoint_accepts_input_path(monkeypatch, tmp_path):
    captured = {}

    def fake_run_python(cmd):
        captured["cmd"] = cmd

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(demo_api, "_run_python", fake_run_python)
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", tmp_path)
    client = TestClient(demo_api.app)

    response = client.post(
        "/api/sample",
        json={
            "count": 12,
            "seed": 3,
            "input_path": "data/raw/MDKG.json",
            "output_name": "mdkg_dev12_sample.json",
        },
    )

    assert response.status_code == 200
    assert captured["cmd"][2] == "scripts/sample_adkg_dev_for_llm.py"
    assert "data/raw/MDKG.json" in captured["cmd"]
    assert str(tmp_path / "mdkg_dev12_sample.json") in captured["cmd"]


def test_errors_endpoint_accepts_gold_path(monkeypatch, tmp_path):
    run_dir = tmp_path / "run1"
    run_dir.mkdir()
    (run_dir / "one_shot_predictions.json").write_text("[]", encoding="utf-8")
    (run_dir / "one_shot_progress.jsonl").write_text("", encoding="utf-8")
    captured = {}

    def fake_run_python(cmd):
        captured["cmd"] = cmd

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(demo_api, "_run_python", fake_run_python)
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", tmp_path)
    client = TestClient(demo_api.app)

    response = client.post(
        "/api/errors",
        json={
            "run_dir_name": "run1",
            "gold_path": "outputs/llm_runs/mdkg_dev100_sample.json",
        },
    )

    assert response.status_code == 200
    assert "outputs/llm_runs/mdkg_dev100_sample.json" in captured["cmd"]


def test_files_endpoint_lists_run_dir_files(tmp_path, monkeypatch):
    run_dir = tmp_path / "run2"
    run_dir.mkdir()
    (run_dir / "metrics.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", tmp_path)
    client = TestClient(demo_api.app)

    response = client.get("/api/files", params={"run_dir_name": "run2"})
    assert response.status_code == 200
    assert response.json()["files"] == ["outputs/llm_runs/run2/metrics.json"]
