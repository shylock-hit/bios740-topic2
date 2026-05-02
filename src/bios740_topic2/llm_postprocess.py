from __future__ import annotations

from typing import Any


def _find_non_overlapping_spans(text: str, needle: str) -> list[tuple[int, int]]:
    spans = []
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            break
        spans.append((index, index + len(needle)))
        start = index + len(needle)
    return spans


def align_entities(text: str, predicted_entities: list[dict[str, str]]) -> list[dict[str, Any]]:
    aligned = []
    seen_spans = set()
    for idx, entity in enumerate(predicted_entities, start=1):
        for start, end in _find_non_overlapping_spans(text, entity["text"]):
            key = (start, end, entity["type"])
            if key in seen_spans:
                continue
            seen_spans.add(key)
            aligned.append(
                {
                    "id": f"P{idx}_{start}_{end}",
                    "type": entity["type"],
                    "start": start,
                    "end": end,
                    "text": text[start:end],
                }
            )
            break
    return aligned


def build_prediction_sample(
    gold_sample: dict[str, Any], payload: dict[str, list[dict[str, str]]]
) -> dict[str, Any]:
    entities = align_entities(gold_sample["text"], payload.get("entities", []))
    by_text: dict[str, list[dict[str, Any]]] = {}
    for entity in entities:
        by_text.setdefault(entity["text"], []).append(entity)

    relations = []
    for relation in payload.get("relations", []):
        head_candidates = by_text.get(relation["head"], [])
        tail_candidates = by_text.get(relation["tail"], [])
        if not head_candidates or not tail_candidates:
            continue
        head = head_candidates[0]
        tail = tail_candidates[0]
        relations.append(
            {
                "type": relation["type"],
                "head": head,
                "tail": tail,
            }
        )

    return {
        "doc_id": gold_sample.get("doc_id"),
        "sent_id": gold_sample["sent_id"],
        "text": gold_sample["text"],
        "entities": entities,
        "relations": relations,
    }
