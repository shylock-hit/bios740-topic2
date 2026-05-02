from __future__ import annotations

from typing import Any


DATASET_TEMPLATES = {
    "ADKG": {
        "raw_input": "data/raw/ADKG.json",
        "sample_file": "outputs/llm_runs/adkg_dev100_sample.json",
        "run_dir": "adkg_dev100_deepseek",
        "gold_path": "outputs/llm_runs/adkg_dev100_sample.json",
    },
    "MDKG": {
        "raw_input": "data/raw/MDKG.json",
        "sample_file": "outputs/llm_runs/mdkg_dev100_sample.json",
        "run_dir": "mdkg_dev100_deepseek",
        "gold_path": "outputs/llm_runs/mdkg_dev100_sample.json",
    },
}


def estimate_eta_from_progress(
    progress: dict[str, Any], rows: list[dict[str, Any]], window_size: int = 10
) -> dict[str, Any]:
    processed = int(progress.get("processed", 0) or 0)
    total = int(progress.get("total", 0) or 0)
    remaining = max(total - processed, 0)
    overall_avg = float(progress.get("avg_latency_seconds", 0.0) or 0.0)

    recent = [float(row.get("latency_seconds", 0.0) or 0.0) for row in rows if row.get("latency_seconds") is not None]
    recent = [value for value in recent if value > 0]

    if len(recent) >= min(3, window_size):
        recent_window = recent[-window_size:]
        recent_avg = sum(recent_window) / len(recent_window)
        source = "recent_window"
    else:
        recent_avg = overall_avg
        source = "overall_average"

    eta_seconds = remaining * recent_avg if remaining > 0 and recent_avg > 0 else 0.0
    return {
        "processed": processed,
        "total": total,
        "remaining": remaining,
        "recent_avg_latency_seconds": recent_avg,
        "overall_avg_latency_seconds": overall_avg,
        "eta_seconds": eta_seconds,
        "source": source,
    }
