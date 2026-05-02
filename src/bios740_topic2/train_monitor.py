from __future__ import annotations

import re


def build_training_command(dataset: str, preset: str, epochs: int, batch_size: int, label: str) -> list[str]:
    dataset_key = dataset.lower()
    if dataset_key not in {"adkg", "mdkg"}:
      raise ValueError(f"Unsupported dataset: {dataset}")
    if preset == "smoke":
        return [
            "python",
            "external/spert/spert.py",
            "train",
            "--train_path",
            f"outputs/spert/{dataset_key}/train.json",
            "--valid_path",
            f"outputs/spert/{dataset_key}/dev.json",
            "--types_path",
            f"outputs/spert/{dataset_key}/types.json",
            "--model_path",
            "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
            "--tokenizer_path",
            "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
            "--save_path",
            f"outputs/checkpoints/{label}",
            "--log_path",
            "outputs/logs",
            "--label",
            label,
            "--epochs",
            str(epochs),
            "--train_batch_size",
            str(batch_size),
            "--eval_batch_size",
            "2",
            "--max_span_size",
            "10",
            "--rel_filter_threshold",
            "0.4",
            "--max_pairs",
            "100",
            "--neg_entity_count",
            "100",
            "--neg_relation_count",
            "100",
            "--store_predictions",
        ]
    return [
        "python",
        "external/spert/spert.py",
        "train",
        "--train_path",
        f"outputs/spert/{dataset_key}/train.json",
        "--valid_path",
        f"outputs/spert/{dataset_key}/dev.json",
        "--types_path",
        f"outputs/spert/{dataset_key}/types.json",
        "--model_path",
        "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
        "--tokenizer_path",
        "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
        "--save_path",
        f"outputs/checkpoints/{dataset_key}",
        "--log_path",
        "outputs/logs",
        "--label",
        label,
        "--epochs",
        str(epochs),
        "--train_batch_size",
        str(batch_size),
        "--eval_batch_size",
        "4",
        "--max_span_size",
        "10",
        "--rel_filter_threshold",
        "0.4",
        "--max_pairs",
        "100",
        "--neg_entity_count",
        "100",
        "--neg_relation_count",
        "100",
        "--store_predictions",
    ]


def parse_training_progress(log_text: str, total_epochs: int) -> dict:
    train_epochs = [int(match) for match in re.findall(r"Train epoch (\d+)", log_text)]
    eval_epochs = [int(match) for match in re.findall(r"Evaluate epoch (\d+)", log_text)]
    current_epoch = max(train_epochs) if train_epochs else max(eval_epochs, default=0)
    completed_epochs = max(eval_epochs, default=0)
    phase = "train" if train_epochs else "eval" if eval_epochs else "idle"
    progress_percent = int(((current_epoch + (1 if phase != "idle" else 0)) / total_epochs) * 100) if total_epochs else 0
    return {
        "current_epoch": current_epoch,
        "completed_epochs": completed_epochs,
        "total_epochs": total_epochs,
        "progress_percent": progress_percent,
        "phase": phase,
    }


def parse_nvidia_smi(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    gpu_name = ""
    memory_used = 0
    memory_total = 0
    gpu_util = 0
    for i, line in enumerate(lines):
        if "NVIDIA" in line and "|" in line:
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 1:
                gpu_name = re.sub(r"^\d+\s+", "", parts[0]).strip()
            if i + 1 < len(lines):
                mem_match = re.search(r"(\d+)MiB / +(\d+)MiB", lines[i + 1])
                util_match = re.search(r"\| +(\d+)% +Default", lines[i + 1])
                if mem_match:
                    memory_used = int(mem_match.group(1))
                    memory_total = int(mem_match.group(2))
                if util_match:
                    gpu_util = int(util_match.group(1))
            break
    return {
        "gpu_name": gpu_name,
        "memory_used_mib": memory_used,
        "memory_total_mib": memory_total,
        "gpu_util_percent": gpu_util,
    }
