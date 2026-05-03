from bios740_topic2.kg_aggregate import aggregate_graph


def test_aggregate_graph_merges_repeated_edges():
    samples = [
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
        },
        {
            "sent_id": "s2",
            "entities": [
                {"id": "e3", "type": "drug", "text": "donepezil"},
                {"id": "e4", "type": "disease", "text": "Alzheimer's disease"},
            ],
            "relations": [
                {
                    "type": "treatment_for",
                    "head": {"id": "e3", "type": "drug", "text": "donepezil"},
                    "tail": {"id": "e4", "type": "disease", "text": "Alzheimer's disease"},
                }
            ],
        },
    ]
    graph = aggregate_graph(samples, top_k_edges=10)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["count"] == 2


def test_aggregate_graph_applies_relation_filter():
    samples = [
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
    graph = aggregate_graph(samples, top_k_edges=10, relation_type="associated_with")
    assert graph["nodes"] == []
    assert graph["edges"] == []
