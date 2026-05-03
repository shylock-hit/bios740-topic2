from fastapi.testclient import TestClient

from bios740_topic2 import demo_api


def test_train_start_endpoint_creates_job(monkeypatch):
    created = {}

    def fake_run_async(record):
        created["record"] = record

    monkeypatch.setattr(demo_api.registry, "run_async", fake_run_async)
    client = TestClient(demo_api.app)
    response = client.post(
        "/api/train/start",
        json={
            "dataset": "ADKG",
            "preset": "smoke",
            "epochs": 1,
            "batch_size": 1,
            "label": "smoke_ui",
        },
    )
    assert response.status_code == 200
    assert created["record"].name == "baseline_training"
    assert created["record"].metadata["dataset"] == "ADKG"


def test_train_status_endpoint_returns_progress(monkeypatch):
    record = demo_api.registry.create(
        "baseline_training",
        ["python", "fake.py"],
        str(demo_api.APP_ROOT),
        metadata={"dataset": "ADKG", "preset": "smoke", "total_epochs": 20},
    )
    record.status = "running"
    record.stdout = "Evaluate epoch 1: 100%|████| 10/10 [00:02<00:00, 5it/s]\n"
    client = TestClient(demo_api.app)
    response = client.get("/api/train/status", params={"job_id": record.id})
    assert response.status_code == 200
    payload = response.json()
    assert payload["job"]["status"] == "running"
    assert payload["progress"]["completed_epochs"] == 1


def test_train_stop_endpoint_marks_job_stopped(monkeypatch):
    record = demo_api.registry.create(
        "baseline_training",
        ["python", "fake.py"],
        str(demo_api.APP_ROOT),
        metadata={"dataset": "ADKG", "preset": "smoke", "total_epochs": 20},
    )
    record.status = "running"

    def fake_stop(job_id):
        assert job_id == record.id
        record.status = "stopped"
        return True

    monkeypatch.setattr(demo_api.registry, "stop", fake_stop)
    client = TestClient(demo_api.app)
    response = client.post("/api/train/stop", json={"job_id": record.id})
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"
