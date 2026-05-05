#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bios740_topic2.shared_schema import (
    build_shared_types,
    filter_dataset_to_schema,
    sample_train_split,
    shared_schema,
)


def load_split_dir(path: Path) -> dict[str, list[dict]]:
    return {
        split: json.loads((path / f"{split}.json").read_text(encoding="utf-8"))
        for split in ("train", "dev", "test")
    }


def write_split_dir(path: Path, dataset: dict[str, list[dict]], types: dict) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for split, samples in dataset.items():
        (path / f"{split}.json").write_text(
            json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    (path / "types.json").write_text(
        json.dumps(types, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_low_resource_train(path: Path, dataset: dict[str, list[dict]], ratio: float, seed: int) -> dict:
    sampled = sample_train_split(dataset, ratio=ratio, seed=seed)
    low_path = path / f"train_{int(ratio * 100)}.json"
    low_path.write_text(
        json.dumps(sampled["train"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return count_items({"train": sampled["train"]})["train"] | {
        "ratio": ratio,
        "seed": seed,
        "path": str(low_path),
    }


def count_items(dataset: dict[str, list[dict]]) -> dict[str, dict[str, int]]:
    return {
        split: {
            "sentences": len(samples),
            "entities": sum(len(sample.get("entities", [])) for sample in samples),
            "relations": sum(len(sample.get("relations", [])) for sample in samples),
        }
        for split, samples in dataset.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create shared-schema SpERT datasets.")
    parser.add_argument("--adkg-dir", default="outputs/spert/adkg")
    parser.add_argument("--mdkg-dir", default="outputs/spert/mdkg")
    parser.add_argument("--output-dir", default="outputs/spert_shared")
    parser.add_argument("--target-ratio", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=740)
    args = parser.parse_args()

    adkg_dir = Path(args.adkg_dir)
    mdkg_dir = Path(args.mdkg_dir)
    output_dir = Path(args.output_dir)

    adkg_types = json.loads((adkg_dir / "types.json").read_text(encoding="utf-8"))
    mdkg_types = json.loads((mdkg_dir / "types.json").read_text(encoding="utf-8"))
    schema = shared_schema(adkg_types, mdkg_types)
    shared_types = build_shared_types(schema["entities"], schema["relations"])

    adkg = filter_dataset_to_schema(load_split_dir(adkg_dir), schema["entities"], schema["relations"])
    mdkg = filter_dataset_to_schema(load_split_dir(mdkg_dir), schema["entities"], schema["relations"])

    write_split_dir(output_dir / "adkg", adkg, shared_types)
    write_split_dir(output_dir / "mdkg", mdkg, shared_types)
    adkg_low = write_low_resource_train(output_dir / "adkg", adkg, args.target_ratio, args.seed)
    mdkg_low = write_low_resource_train(output_dir / "mdkg", mdkg, args.target_ratio, args.seed)

    summary = {
        "shared_entities": sorted(schema["entities"]),
        "shared_relations": sorted(schema["relations"]),
        "target_ratio": args.target_ratio,
        "seed": args.seed,
        "adkg": count_items(adkg),
        "mdkg": count_items(mdkg),
        "low_resource_train": {
            "adkg": adkg_low,
            "mdkg": mdkg_low,
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
