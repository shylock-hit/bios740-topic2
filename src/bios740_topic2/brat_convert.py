from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def parse_brat_ann(path: str | Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    entities: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        parts = line.split("\t")
        if line.startswith("T") and len(parts) >= 3:
            entity_id = parts[0]
            meta = parts[1].split()
            if len(meta) < 3 or ";" in parts[1]:
                continue
            entity_type, start, end = meta[0], int(meta[1]), int(meta[2])
            entities.append(
                {
                    "id": entity_id,
                    "type": normalize_entity_type(entity_type),
                    "start": start,
                    "end": end,
                    "text": parts[2],
                }
            )
        elif line.startswith("R") and len(parts) >= 2:
            meta = parts[1].split()
            if len(meta) < 3:
                continue
            relation_type = normalize_relation_type(meta[0])
            arg1 = meta[1].split(":", 1)[1]
            arg2 = meta[2].split(":", 1)[1]
            relations.append(
                {"id": parts[0], "type": relation_type, "head_id": arg1, "tail_id": arg2}
            )
    return entities, relations


def normalize_entity_type(label: str) -> str:
    mapping = {
        "Anatomy": "region",
        "Phenotype": "symptom",
        "Sign": "signs",
        "Method/Procedure": "method",
        "Gene/Protein": "gene",
        "Disease/Symptom": "disease",
        "Drug/Chemical": "drug",
        "Health": "Health_factors",
        "Health_factors": "Health_factors",
    }
    return mapping.get(label, label)


def normalize_relation_type(label: str) -> str:
    mapping = {
        "Risk": "risk_factor_of",
        "Diagnostic": "help_diagnose",
        "Characteristic": "characteristic_of",
        "Association": "associated_with",
        "Therapeutic": "treatment_for",
        "Hierarchical": "hyponym_of",
        "Abbreviation": "abbreviation_for",
    }
    return mapping.get(label, label)


def sentence_spans(text: str) -> list[tuple[int, int]]:
    try:
        import pysbd

        segmenter = pysbd.Segmenter(language="en", clean=False, char_span=True)
        spans = []
        for span in segmenter.segment(text):
            start = span.start
            end = span.end
            if text[start:end].strip():
                left = start + len(text[start:end]) - len(text[start:end].lstrip())
                right = end - (len(text[start:end]) - len(text[start:end].rstrip()))
                spans.append((left, right))
        return spans
    except Exception:
        pass

    spans: list[tuple[int, int]] = []
    start = 0
    for match in re.finditer(r"(?<=[.!?])\s+", text):
        end = match.start()
        if text[start:end].strip():
            left = start + len(text[start:end]) - len(text[start:end].lstrip())
            spans.append((left, end))
        start = match.end()
    if text[start:].strip():
        left = start + len(text[start:]) - len(text[start:].lstrip())
        spans.append((left, len(text)))
    return spans


def convert_document(txt_path: str | Path, ann_path: str | Path) -> list[dict[str, Any]]:
    txt_path = Path(txt_path)
    text = txt_path.read_text(encoding="utf-8")
    entities, relations = parse_brat_ann(ann_path)
    entities_by_id = {entity["id"]: entity for entity in entities}
    samples = []

    for sent_index, (sent_start, sent_end) in enumerate(sentence_spans(text)):
        sent_entities = [
            entity
            for entity in entities
            if sent_start <= entity["start"] and entity["end"] <= sent_end
        ]
        sent_ids = {entity["id"] for entity in sent_entities}
        sample_entities = [
            {
                **entity,
                "start": entity["start"] - sent_start,
                "end": entity["end"] - sent_start,
                "text": text[entity["start"] : entity["end"]],
            }
            for entity in sent_entities
        ]
        local_entity_by_id = {entity["id"]: entity for entity in sample_entities}

        sample_relations = []
        for relation in relations:
            if relation["head_id"] not in sent_ids or relation["tail_id"] not in sent_ids:
                continue
            head = entities_by_id[relation["head_id"]]
            tail = entities_by_id[relation["tail_id"]]
            sample_relations.append(
                {
                    "type": relation["type"],
                    "head": local_entity_by_id[head["id"]],
                    "tail": local_entity_by_id[tail["id"]],
                }
            )

        samples.append(
            {
                "doc_id": txt_path.stem,
                "sent_id": f"{txt_path.stem}_s{sent_index}",
                "text": text[sent_start:sent_end],
                "entities": sample_entities,
                "relations": sample_relations,
            }
        )
    return samples


def convert_brat_directory(
    source_dir: str | Path, train_ratio: float = 0.7, dev_ratio: float = 0.15
) -> dict[str, list[dict[str, Any]]]:
    source = Path(source_dir)
    doc_ids = sorted(path.stem for path in source.glob("*.txt") if (source / f"{path.stem}.ann").exists())
    all_samples_by_doc = [
        convert_document(source / f"{doc_id}.txt", source / f"{doc_id}.ann") for doc_id in doc_ids
    ]
    train_cut = round(len(doc_ids) * train_ratio)
    dev_cut = round(len(doc_ids) * (train_ratio + dev_ratio))
    dataset = {"train": [], "dev": [], "test": []}
    for index, samples in enumerate(all_samples_by_doc):
        split = "train" if index < train_cut else "dev" if index < dev_cut else "test"
        dataset[split].extend(samples)
    return dataset
