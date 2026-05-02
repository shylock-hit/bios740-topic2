import json
from pathlib import Path

from fastapi.testclient import TestClient

from bios740_topic2 import demo_api


def test_sample_endpoint_accepts_input_path(monkeypatch, tmp_path):
    captured = {}
    output_root = demo_api.APP_ROOT / "outputs" / "llm_runs" / "_pytest_sample"
    output_root.mkdir(parents=True, exist_ok=True)

    def fake_run_python(cmd):
        captured["cmd"] = cmd

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(demo_api, "_run_python", fake_run_python)
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", output_root)
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
    assert captured["cmd"][1] == "scripts/sample_dev_for_llm.py"
    assert "data/raw/MDKG.json" in captured["cmd"]
    assert str(output_root / "mdkg_dev12_sample.json") in captured["cmd"]


def test_errors_endpoint_accepts_gold_path(monkeypatch, tmp_path):
    run_dir = demo_api.APP_ROOT / "outputs" / "llm_runs" / "_pytest_run1"
    run_dir.mkdir(exist_ok=True)
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
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", run_dir.parent)
    client = TestClient(demo_api.app)

    response = client.post(
        "/api/errors",
        json={
            "run_dir_name": "_pytest_run1",
            "gold_path": "outputs/llm_runs/mdkg_dev100_sample.json",
        },
    )

    assert response.status_code == 200
    assert "outputs/llm_runs/mdkg_dev100_sample.json" in captured["cmd"]


def test_files_endpoint_lists_run_dir_files(tmp_path, monkeypatch):
    run_dir = demo_api.APP_ROOT / "outputs" / "llm_runs" / "_pytest_run2"
    run_dir.mkdir(exist_ok=True)
    (run_dir / "metrics.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", run_dir.parent)
    client = TestClient(demo_api.app)

    response = client.get("/api/files", params={"run_dir_name": "_pytest_run2"})
    assert response.status_code == 200
    assert response.json()["files"] == ["outputs/llm_runs/_pytest_run2/metrics.json"]
