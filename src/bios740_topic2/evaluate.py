from __future__ import annotations

from collections import defaultdict
from typing import Any


def _entity_key(sample: dict[str, Any], entity: dict[str, Any]) -> tuple[str, int, int, str]:
    return (sample["sent_id"], entity["start"], entity["end"], entity["type"])


def _relation_key(sample: dict[str, Any], relation: dict[str, Any]) -> tuple:
    return (
        sample["sent_id"],
        relation["type"],
        relation["head"]["id"],
        relation["tail"]["id"],
        relation["head"]["start"],
        relation["head"]["end"],
        relation["tail"]["start"],
        relation["tail"]["end"],
    )


def prf(tp: int, predicted: int, gold: int) -> dict[str, float]:
    precision = tp / predicted if predicted else 0.0
    recall = tp / gold if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 6), "recall": round(recall, 6), "f1": round(f1, 6)}


def _score_sets(gold_set: set[tuple], predicted_set: set[tuple]) -> dict[str, float]:
    return prf(len(gold_set & predicted_set), len(predicted_set), len(gold_set))


def evaluate_dataset(
    gold_samples: list[dict[str, Any]], predicted_samples: list[dict[str, Any]]
) -> dict[str, Any]:
    gold_by_id = {sample["sent_id"]: sample for sample in gold_samples}
    pred_by_id = {sample["sent_id"]: sample for sample in predicted_samples}

    gold_entities = {
        _entity_key(sample, entity) for sample in gold_samples for entity in sample.get("entities", [])
    }
    pred_entities = {
        _entity_key(gold_by_id.get(sample["sent_id"], sample), entity)
        for sample in predicted_samples
        for entity in sample.get("entities", [])
    }
    gold_relations = {
        _relation_key(sample, relation)
        for sample in gold_samples
        for relation in sample.get("relations", [])
    }
    pred_relations = {
        _relation_key(gold_by_id.get(sample["sent_id"], sample), relation)
        for sample in predicted_samples
        for relation in sample.get("relations", [])
    }

    return {
        "entities": {
            "micro": _score_sets(gold_entities, pred_entities),
            "by_type": _score_by_type(gold_entities, pred_entities, type_index=3),
        },
        "relations": {
            "micro": _score_sets(gold_relations, pred_relations),
            "by_type": _score_by_type(gold_relations, pred_relations, type_index=1),
        },
        "sentence_count": len(gold_by_id),
        "predicted_sentence_count": len(pred_by_id),
    }


def _score_by_type(
    gold_set: set[tuple], predicted_set: set[tuple], type_index: int
) -> dict[str, dict[str, float]]:
    labels = sorted({item[type_index] for item in gold_set | predicted_set})
    results = {}
    for label in labels:
        gold_label = {item for item in gold_set if item[type_index] == label}
        pred_label = {item for item in predicted_set if item[type_index] == label}
        results[label] = _score_sets(gold_label, pred_label)
    return results


def boundary_errors(
    gold_samples: list[dict[str, Any]], predicted_samples: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    predicted_by_sent = defaultdict(list)
    for sample in predicted_samples:
        predicted_by_sent[sample["sent_id"]].extend(sample.get("entities", []))

    errors = []
    for sample in gold_samples:
        for gold_entity in sample.get("entities", []):
            for pred_entity in predicted_by_sent[sample["sent_id"]]:
                same_type = gold_entity["type"] == pred_entity["type"]
                overlaps = gold_entity["start"] < pred_entity["end"] and pred_entity["start"] < gold_entity["end"]
                exact = (
                    gold_entity["start"] == pred_entity["start"]
                    and gold_entity["end"] == pred_entity["end"]
                )
                if same_type and overlaps and not exact:
                    errors.append(
                        {
                            "sent_id": sample["sent_id"],
                            "type": gold_entity["type"],
                            "gold_text": gold_entity["text"],
                            "pred_text": pred_entity["text"],
                            "gold_span": [gold_entity["start"], gold_entity["end"]],
                            "pred_span": [pred_entity["start"], pred_entity["end"]],
                        }
                    )
    return errors

