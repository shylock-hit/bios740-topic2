import json

from fastapi.testclient import TestClient

from bios740_topic2 import demo_api


def test_kg_graph_endpoint_returns_aggregated_graph(tmp_path, monkeypatch):
    run_dir = demo_api.APP_ROOT / "outputs" / "llm_runs" / "_pytest_kg_run"
    run_dir.mkdir(exist_ok=True)
    payload = [
        {
            "sent_id": "s1",
            "entities": [
                {"id": "e1", "type": "drug", "text": "Donepezil"},
                {"id": "e2", "type": "disease", "text": "Alzheimer's disease"},
            ],
            "relations": [
                {
                    "type": "treatment_for",
                    "head": {"id": "e1", "type": "drug", "text": "Donepezil"},
                    "tail": {"id": "e2", "type": "disease", "text": "Alzheimer's disease"},
                }
            ],
        }
    ]
    (run_dir / "one_shot_predictions.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", run_dir.parent)
    client = TestClient(demo_api.app)
    response = client.get("/api/kg/graph", params={"run_dir_name": "_pytest_kg_run", "mode": "one_shot"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["nodes"]) == 2
    assert len(body["edges"]) == 1


def test_kg_relations_endpoint_returns_relation_types(monkeypatch):
    run_dir = demo_api.APP_ROOT / "outputs" / "llm_runs" / "_pytest_kg_rel"
    run_dir.mkdir(exist_ok=True)
    payload = [
        {
            "sent_id": "s1",
            "entities": [
                {"id": "e1", "type": "drug", "text": "Donepezil"},
                {"id": "e2", "type": "disease", "text": "Alzheimer's disease"},
            ],
            "relations": [
                {
                    "type": "treatment_for",
                    "head": {"id": "e1", "type": "drug", "text": "Donepezil"},
                    "tail": {"id": "e2", "type": "disease", "text": "Alzheimer's disease"},
                },
                {
                    "type": "associated_with",
                    "head": {"id": "e1", "type": "drug", "text": "Donepezil"},
                    "tail": {"id": "e2", "type": "disease", "text": "Alzheimer's disease"},
                },
            ],
        }
    ]
    (run_dir / "one_shot_predictions.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(demo_api, "OUTPUT_ROOT", run_dir.parent)
    client = TestClient(demo_api.app)
    response = client.get("/api/kg/relations", params={"run_dir_name": "_pytest_kg_rel", "mode": "one_shot"})
    assert response.status_code == 200
    assert response.json()["relation_types"] == ["associated_with", "treatment_for"]
