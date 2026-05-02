#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt
import pandas as pd

from bios740_topic2.data_io import load_dataset


def flatten(dataset: dict[str, list[dict]]) -> list[dict]:
    return [sample for split in dataset.values() for sample in split]


def entity_counts(samples: list[dict]) -> Counter:
    counts = Counter()
    for sample in samples:
        for entity in sample.get("entities", []):
            counts[entity["type"]] += 1
    return counts


def unique_entity_counts(samples: list[dict]) -> Counter:
    values = defaultdict(set)
    for sample in samples:
        for entity in sample.get("entities", []):
            values[entity["type"]].add(entity["text"].lower())
    return Counter({key: len(value) for key, value in values.items()})


def relation_counts(samples: list[dict]) -> Counter:
    counts = Counter()
    for sample in samples:
        for relation in sample.get("relations", []):
            counts[relation["type"]] += 1
    return counts


def relation_pair_matrix(samples: list[dict]) -> pd.DataFrame:
    counts = Counter()
    for sample in samples:
        for relation in sample.get("relations", []):
            head_type = relation["head"]["type"]
            tail_type = relation["tail"]["type"]
            counts[(head_type, tail_type)] += 1
    labels = sorted({label for pair in counts for label in pair})
    matrix = pd.DataFrame(0, index=labels, columns=labels)
    for (head, tail), count in counts.items():
        matrix.loc[head, tail] = count
    return matrix


def distance_bins(samples: list[dict]) -> pd.DataFrame:
    rows = []
    for sample in samples:
        for relation in sample.get("relations", []):
            distance = abs(relation["head"]["start"] - relation["tail"]["start"])
            rows.append({"relation_type": relation["type"], "char_distance": distance})
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["bin", "relations"])
    bins = [0, 25, 50, 100, 200, 10_000]
    labels = ["0-25", "26-50", "51-100", "101-200", ">200"]
    df["bin"] = pd.cut(df["char_distance"], bins=bins, labels=labels, include_lowest=True)
    return df.groupby("bin", observed=False).size().reset_index(name="relations")


def sentence_stats(samples: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sent_id": sample["sent_id"],
                "tokens": len(sample["text"].split()),
                "entities": len(sample.get("entities", [])),
                "relations": len(sample.get("relations", [])),
            }
            for sample in samples
        ]
    )


def bar_plot(series: pd.Series, title: str, ylabel: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    series.sort_values(ascending=False).plot(kind="bar", ax=ax, color="#4C78A8")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def hist_plot(values: pd.Series, title: str, xlabel: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(values, bins=30, color="#59A14F", edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Sentences")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def heatmap(matrix: pd.DataFrame, title: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(matrix.values, cmap="Blues")
    ax.set_title(title)
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    for i in range(len(matrix.index)):
        for j in range(len(matrix.columns)):
            value = int(matrix.iloc[i, j])
            if value:
                ax.text(j, i, str(value), ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def process_dataset(name: str, path: Path, output_dir: Path) -> dict[str, str]:
    dataset = load_dataset(path)
    samples = flatten(dataset)
    prefix = name.lower()

    entities = pd.Series(entity_counts(samples), name="count")
    unique_entities = pd.Series(unique_entity_counts(samples), name="unique_count")
    relations = pd.Series(relation_counts(samples), name="count")
    sentence_df = sentence_stats(samples)
    pair_matrix = relation_pair_matrix(samples)
    distance_df = distance_bins(samples)

    entities.to_csv(output_dir / f"{prefix}_entity_counts.csv", header=True)
    unique_entities.to_csv(output_dir / f"{prefix}_unique_entity_counts.csv", header=True)
    relations.to_csv(output_dir / f"{prefix}_relation_counts.csv", header=True)
    sentence_df.to_csv(output_dir / f"{prefix}_sentence_stats.csv", index=False)
    pair_matrix.to_csv(output_dir / f"{prefix}_relation_pair_matrix.csv")
    distance_df.to_csv(output_dir / f"{prefix}_relation_distance_bins.csv", index=False)

    bar_plot(entities, f"{name} Entity Type Counts", "Entities", output_dir / f"{prefix}_entity_counts.png")
    bar_plot(relations, f"{name} Relation Type Counts", "Relations", output_dir / f"{prefix}_relation_counts.png")
    hist_plot(sentence_df["tokens"], f"{name} Sentence Length Distribution", "Tokens", output_dir / f"{prefix}_sentence_lengths.png")
    hist_plot(sentence_df["entities"], f"{name} Entities per Sentence", "Entities", output_dir / f"{prefix}_entities_per_sentence.png")
    heatmap(pair_matrix, f"{name} Relation Entity-Type Pair Counts", output_dir / f"{prefix}_relation_pair_heatmap.png")
    bar_plot(distance_df.set_index("bin")["relations"], f"{name} Relation Distance Bins", "Relations", output_dir / f"{prefix}_relation_distance_bins.png")

    return {
        "sentences": str(len(samples)),
        "entities": str(int(entities.sum())),
        "unique_entities": str(int(unique_entities.sum())),
        "relations": str(int(relations.sum())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate report tables and figures.")
    parser.add_argument("--adkg", default="data/raw/ADKG.json")
    parser.add_argument("--mdkg", default="data/raw/MDKG.json")
    parser.add_argument("--output-dir", default="outputs/report_artifacts")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "ADKG": process_dataset("ADKG", Path(args.adkg), output_dir),
        "MDKG": process_dataset("MDKG", Path(args.mdkg), output_dir),
    }
    (output_dir / "artifact_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_lines = ["# Report Artifact Index", ""]
    for image in sorted(output_dir.glob("*.png")):
        md_lines.append(f"- `{image.name}`")
    (output_dir / "artifact_index.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote report artifacts to {output_dir}")


if __name__ == "__main__":
    main()

