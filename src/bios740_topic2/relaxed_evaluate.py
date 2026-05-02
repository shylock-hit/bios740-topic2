from __future__ import annotations

from typing import Any

from bios740_topic2.evaluate import prf


def _overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


def relaxed_entity_metrics(
    gold_samples: list[dict[str, Any]], predicted_samples: list[dict[str, Any]]
) -> dict[str, float]:
    gold_entities = [
        (sample["sent_id"], entity["start"], entity["end"], entity["type"])
        for sample in gold_samples
        for entity in sample.get("entities", [])
    ]
    pred_entities = [
        (sample["sent_id"], entity["start"], entity["end"], entity["type"])
        for sample in predicted_samples
        for entity in sample.get("entities", [])
    ]
    matched = set()
    tp = 0
    for pred in pred_entities:
        for gold_index, gold in enumerate(gold_entities):
            if gold_index in matched:
                continue
            if pred[0] == gold[0] and pred[3] == gold[3] and _overlaps(pred[1], pred[2], gold[1], gold[2]):
                matched.add(gold_index)
                tp += 1
                break
    return prf(tp, len(pred_entities), len(gold_entities))


def relaxed_relation_metrics(
    gold_samples: list[dict[str, Any]], predicted_samples: list[dict[str, Any]]
) -> dict[str, float]:
    gold_relations = [
        (
            sample["sent_id"],
            relation["type"],
            relation["head"]["start"],
            relation["head"]["end"],
            relation["tail"]["start"],
            relation["tail"]["end"],
        )
        for sample in gold_samples
        for relation in sample.get("relations", [])
    ]
    pred_relations = [
        (
            sample["sent_id"],
            relation["type"],
            relation["head"]["start"],
            relation["head"]["end"],
            relation["tail"]["start"],
            relation["tail"]["end"],
        )
        for sample in predicted_samples
        for relation in sample.get("relations", [])
    ]
    matched = set()
    tp = 0
    for pred in pred_relations:
        for gold_index, gold in enumerate(gold_relations):
            if gold_index in matched:
                continue
            same_sent = pred[0] == gold[0]
            same_type = pred[1] == gold[1]
            head_overlap = _overlaps(pred[2], pred[3], gold[2], gold[3])
            tail_overlap = _overlaps(pred[4], pred[5], gold[4], gold[5])
            if same_sent and same_type and head_overlap and tail_overlap:
                matched.add(gold_index)
                tp += 1
                break
    return prf(tp, len(pred_relations), len(gold_relations))
