from __future__ import annotations

import re
from collections import Counter
from typing import Any


def _normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^\w\s-]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _node_key(entity: dict[str, Any]) -> tuple[str, str]:
    return (_normalize_text(entity.get("text", "")), entity.get("type", "other"))


def aggregate_graph(
    samples: list[dict[str, Any]],
    top_k_edges: int = 50,
    relation_type: str | None = None,
    min_edge_count: int = 1,
) -> dict[str, Any]:
    node_counter: Counter[tuple[str, str]] = Counter()
    node_display: dict[tuple[str, str], str] = {}
    edge_counter: Counter[tuple[tuple[str, str], str, tuple[str, str]]] = Counter()

    for sample in samples:
        for entity in sample.get("entities", []):
            key = _node_key(entity)
            if not key[0]:
                continue
            node_counter[key] += 1
            node_display.setdefault(key, entity.get("text", key[0]))

        for relation in sample.get("relations", []):
            if relation_type and relation.get("type") != relation_type:
                continue
            head_key = _node_key(relation.get("head", {}))
            tail_key = _node_key(relation.get("tail", {}))
            if not head_key[0] or not tail_key[0]:
                continue
            edge_counter[(head_key, relation.get("type", "related_to"), tail_key)] += 1

    filtered_edges = [
        (edge_key, count) for edge_key, count in edge_counter.most_common(top_k_edges) if count >= min_edge_count
    ]
    active_nodes = {head for (head, _, _), _ in filtered_edges} | {tail for (_, _, tail), _ in filtered_edges}

    nodes = [
        {
            "id": f"{node_type}:{normalized}",
            "label": node_display[(normalized, node_type)],
            "type": node_type,
            "count": node_counter[(normalized, node_type)],
        }
        for normalized, node_type in active_nodes
    ]

    edges = [
        {
            "source": f"{head[1]}:{head[0]}",
            "target": f"{tail[1]}:{tail[0]}",
            "relation": relation,
            "count": count,
        }
        for (head, relation, tail), count in filtered_edges
    ]

    relation_counts = Counter(edge["relation"] for edge in edges)
    return {
        "nodes": sorted(nodes, key=lambda item: (-item["count"], item["label"])),
        "edges": edges,
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "top_relation": relation_counts.most_common(1)[0][0] if relation_counts else None,
        },
    }
