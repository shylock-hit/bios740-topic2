#!/usr/bin/env python
"""Generate architecture and pipeline diagrams for the report.

Outputs:
  report/figures/spert_architecture.png    — SpERT model architecture
  report/figures/pipeline_flow.png         — End-to-end pipeline flow
  report/figures/agentic_annotation.png    — Agentic data annotation workflow
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "report" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color palette
C_BLUE = "#4C78A8"
C_GREEN = "#59A14F"
C_ORANGE = "#E45756"
C_PURPLE = "#B07AA1"
C_TEAL = "#499894"
C_YELLOW = "#F58518"
C_GRAY = "#9D9D9D"
C_LIGHT = "#EDC948"
C_BG = "#FAFAFA"


def _box(ax, x, y, w, h, label, color=C_BLUE, fontsize=9, textcolor="white", alpha=0.9):
    """Draw a rounded box with centered text."""
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.03",
        facecolor=color, edgecolor="white", linewidth=1.5, alpha=alpha,
        zorder=3,
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color=textcolor, zorder=4)


def _arrow(ax, x1, y1, x2, y2, color=C_GRAY, style="->", lw=1.5):
    """Draw a simple arrow."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw),
                zorder=2)


def _label(ax, x, y, text, fontsize=7.5, color="#333"):
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=color, style="italic", zorder=5)


# ─── SpERT Architecture ──────────────────────────────────────────────────

def draw_spert_architecture():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)

    # Title
    ax.text(6, 7.6, "SpERT Architecture with PubMedBERT Encoder",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#222")

    # ── Input ──
    _box(ax, 1.5, 6.5, 2.2, 0.65, "Input Sentence\nTokens", C_GRAY, 8.5, "#333")

    # ── PubMedBERT ──
    _box(ax, 1.5, 5.0, 2.4, 1.0, "PubMedBERT\nEncoder\n(12-layer Transformer)", C_BLUE, 9)
    _arrow(ax, 1.5, 6.15, 1.5, 5.55)

    # ── Token embeddings ──
    _box(ax, 4.5, 6.5, 2.0, 0.55, "Contextual Token\nEmbeddings", C_TEAL, 8.5)
    _arrow(ax, 2.75, 5.0, 3.5, 6.3)

    # ── Span enumeration ──
    _box(ax, 4.5, 5.2, 2.0, 0.65, "Span Enumeration\n(max_len=10)", C_PURPLE, 8.5)
    _arrow(ax, 4.5, 6.2, 4.5, 5.55)

    # ── Span representation ──
    _box(ax, 4.5, 3.9, 2.2, 0.8, "Span Representation\n[start] + [end]\n+ Width Embedding", C_ORANGE, 8)
    _arrow(ax, 4.5, 4.85, 4.5, 4.35)

    # ── Entity classifier ──
    _box(ax, 4.5, 2.5, 2.0, 0.65, "Entity Type\nClassifier (FFN)", C_GREEN, 8.5)
    _arrow(ax, 4.5, 3.45, 4.5, 2.85)

    # ── Entity output ──
    _box(ax, 4.5, 1.3, 2.2, 0.65, "Entity Predictions\n(type / none)", C_TEAL, 8.5)
    _arrow(ax, 4.5, 2.15, 4.5, 1.65)

    # ── Relation section ──
    # Head & Tail entity pair
    _box(ax, 8.2, 6.5, 2.2, 0.55, "Candidate Entity Pairs\n(head, tail)", C_PURPLE, 8)
    _arrow(ax, 5.6, 1.3, 7.1, 6.3, style="->", lw=1.2)

    # Context between entities
    _box(ax, 8.2, 5.2, 2.4, 0.8, "Relation Representation\n[head] + [context]\n+ [tail]", C_ORANGE, 8)
    _arrow(ax, 8.2, 6.2, 8.2, 5.65)

    # Context embedding from token embeddings
    _box(ax, 8.2, 3.9, 2.0, 0.55, "Avg Context\nEmbedding", C_TEAL, 8)
    _arrow(ax, 8.2, 4.75, 8.2, 4.2)
    _label(ax, 6.5, 6.5, "from token\nembeddings", 7)

    # Relation classifier
    _box(ax, 8.2, 2.5, 2.0, 0.65, "Relation Type\nClassifier (FFN)", C_GREEN, 8.5)
    _arrow(ax, 8.2, 3.6, 8.2, 2.85)

    # Relation output
    _box(ax, 8.2, 1.3, 2.2, 0.65, "Relation Predictions\n(type / none)", C_YELLOW, 8.5, "#333")
    _arrow(ax, 8.2, 2.15, 8.2, 1.65)

    # ── Negative sampling annotation ──
    ax.annotate(
        "Negative Sampling\n(entity: 100 / sent\nrelation: 10 / sent)",
        xy=(4.5, 3.1), xytext=(10.8, 3.1),
        fontsize=7.5, ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3E0", edgecolor=C_ORANGE, lw=1),
        zorder=5,
    )

    # ── Legend ──
    legend_items = [
        mpatches.Patch(color=C_BLUE, label="Pretrained Encoder"),
        mpatches.Patch(color=C_PURPLE, label="Enumeration / Selection"),
        mpatches.Patch(color=C_ORANGE, label="Representation"),
        mpatches.Patch(color=C_GREEN, label="Classification"),
        mpatches.Patch(color=C_TEAL, label="Output / Embedding"),
    ]
    ax.legend(handles=legend_items, loc="lower left", fontsize=7.5,
              framealpha=0.9, edgecolor="#CCC")

    fig.tight_layout(pad=0.5)
    out = OUTPUT_DIR / "spert_architecture.png"
    fig.savefig(out, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {out}")


# ─── Pipeline Flow ────────────────────────────────────────────────────────

def draw_pipeline_flow():
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)

    ax.text(6.5, 4.6, "End-to-End Biomedical NER/RE Pipeline",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#222")

    # Row 1: Data pipeline
    stages = [
        (1.2, 3.2, "Raw JSON\n(ADKG / MDKG)", C_GRAY, "#333"),
        (3.6, 3.2, "Data\nValidation", C_PURPLE),
        (6.0, 3.2, "EDA\n(Distributions)", C_TEAL),
        (8.4, 3.2, "SpERT Format\nConversion", C_ORANGE),
        (10.8, 3.2, "types.json\n+ Split Files", C_GREEN),
    ]

    for i, (x, y, label, color, *tc) in enumerate(stages):
        textcolor = tc[0] if tc else "white"
        _box(ax, x, y, 1.9, 0.85, label, color, 8.5, textcolor)
        if i > 0:
            _arrow(ax, stages[i-1][0] + 1.0, y, x - 1.0, y)

    # Row 2: Training & evaluation
    stages2 = [
        (1.2, 1.4, "SpERT\nTraining\n(PubMedBERT)", C_BLUE),
        (3.8, 1.4, "Model\nCheckpoint", C_GREEN),
        (6.4, 1.4, "Prediction\nInference", C_PURPLE),
        (9.0, 1.4, "Strict\nEvaluation\n(P / R / F1)", C_ORANGE),
        (11.5, 1.4, "Report\nTables &\nFigures", C_TEAL),
    ]

    for i, (x, y, label, color, *tc) in enumerate(stages2):
        textcolor = tc[0] if tc else "white"
        _box(ax, x, y, 1.9, 1.0, label, color, 8.5, textcolor)
        if i > 0:
            _arrow(ax, stages2[i-1][0] + 1.0, y, x - 1.0, y)

    # Vertical arrows connecting rows
    _arrow(ax, 10.8, 2.75, 10.8, 2.0, C_GRAY, "->", 1.2)  # types.json → skip
    _arrow(ax, 10.8, 2.75, 1.2, 2.0, C_GRAY, "->", 1.0)   # → training
    _label(ax, 5.5, 2.35, "converted data feeds into training", 7)

    # Scripts annotation
    script_labels = [
        (1.2, 0.55, "scripts/eda.py"),
        (3.6, 0.55, "scripts/convert_to_spert.py"),
        (1.2, 0.2, "scripts/train_spert.sh"),
        (6.4, 0.55, "spert/spert.py"),
        (9.0, 0.55, "scripts/evaluate_predictions.py"),
    ]
    for x, y, label in script_labels:
        ax.text(x, y, label, ha="center", va="center", fontsize=6.5,
                color="#666", family="monospace")

    fig.tight_layout(pad=0.5)
    out = OUTPUT_DIR / "pipeline_flow.png"
    fig.savefig(out, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {out}")


# ─── Agentic Data Annotation Workflow ─────────────────────────────────────

def draw_agentic_annotation():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)

    ax.text(7, 8.6, "Agentic Workflow: One-Shot vs. 3-Step LLM Annotation",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#222")

    # ═══════════════════════════════════════════════════════════
    # LEFT BRANCH: One-Shot Extraction
    # ═══════════════════════════════════════════════════════════

    # Column header
    ax.text(3.2, 8.0, "Mode 1: One-Shot (run_one_shot)", ha="center", fontsize=10,
            fontweight="bold", color=C_BLUE,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#E3F2FD", edgecolor=C_BLUE, lw=1.2))

    # Input
    _box(ax, 3.2, 7.1, 2.6, 0.7, "ADKG Dev\nSentences (100)", C_GRAY, 9, "#333")
    _arrow(ax, 3.2, 6.7, 3.2, 6.15)

    # System prompt
    _box(ax, 3.2, 5.7, 2.8, 0.75, "System Prompt\n(ADKG schema +\nJSON format)", C_PURPLE, 8)
    _arrow(ax, 3.2, 5.28, 3.2, 4.75)

    # One-shot call
    _box(ax, 3.2, 4.3, 2.8, 0.8, "one_shot\nLLM API Call\n(extract entities\n+ relations)", C_BLUE, 8.5)
    _arrow(ax, 3.2, 3.85, 3.2, 3.3)

    # Normalize
    _box(ax, 3.2, 2.9, 2.6, 0.65, "llm_schema\nnormalize_payload\n+ validate", C_TEAL, 8)
    _arrow(ax, 3.2, 2.5, 3.2, 2.0)

    # Postprocess
    _box(ax, 3.2, 1.6, 2.6, 0.65, "llm_postprocess\nspan alignment\n+ relation linking", C_ORANGE, 7.5)
    _arrow(ax, 3.2, 1.2, 3.2, 0.65)

    # Output
    _box(ax, 3.2, 0.3, 2.6, 0.6, "one_shot_\npredictions.json", C_GREEN, 8)

    # ═══════════════════════════════════════════════════════════
    # RIGHT BRANCH: 3-Step Agent Workflow
    # ═══════════════════════════════════════════════════════════

    # Column header
    ax.text(10.2, 8.0, "Mode 2: 3-Step Workflow (run_entities_then_relations)", ha="center", fontsize=10,
            fontweight="bold", color=C_ORANGE,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFF3E0", edgecolor=C_ORANGE, lw=1.2))

    # Input (shared)
    _box(ax, 10.2, 7.1, 2.6, 0.7, "ADKG Dev\nSentences (100)", C_GRAY, 9, "#333")
    _arrow(ax, 10.2, 6.7, 10.2, 6.15)

    # System prompt (shared)
    _box(ax, 10.2, 5.7, 2.8, 0.75, "System Prompt\n(ADKG schema +\nJSON format)", C_PURPLE, 8)
    _arrow(ax, 10.2, 5.28, 10.2, 4.85)

    # Step 1: extract_entities
    _box(ax, 10.2, 4.4, 2.8, 0.8, "Step 1: extract_entities\nLLM API Call\n(entities only,\nrelations=[])", C_BLUE, 8)
    _arrow(ax, 10.2, 3.95, 10.2, 3.45)

    # Step 2: extract_relations
    _box(ax, 10.2, 3.05, 2.8, 0.75, "Step 2: extract_relations\nLLM API Call\n(given entity list,\nrelations only)", C_ORANGE, 7.5)
    _label(ax, 12.2, 3.5, "entity list\nfrom step 1", 6.5)
    _arrow(ax, 10.2, 2.6, 10.2, 2.1)

    # Step 3: review_and_fix
    _box(ax, 10.2, 1.65, 2.8, 0.8, "Step 3: review_and_fix\nLLM API Call\n(review entities +\nrelations, fix errors)", C_TEAL, 7.5)
    _label(ax, 12.2, 2.1, "entities +\nrelations\nfrom steps 1&2", 6)
    _arrow(ax, 10.2, 1.2, 10.2, 0.65)

    # Output
    _box(ax, 10.2, 0.3, 2.6, 0.6, "workflow_\npredictions.json", C_GREEN, 8)

    # ═══════════════════════════════════════════════════════════
    # CENTER: Evaluation
    # ═══════════════════════════════════════════════════════════

    # Merge point
    _arrow(ax, 4.6, 0.3, 6.2, 0.3, C_GRAY, "->", 1.2)
    _arrow(ax, 8.8, 0.3, 7.2, 0.3, C_GRAY, "->", 1.2)

    # Strict eval
    _box(ax, 6.7, 1.3, 2.2, 0.65, "Strict Evaluation\n(exact span +\ndirected endpoints)", C_BLUE, 7.5)

    # Relaxed eval
    _box(ax, 6.7, 0.35, 2.2, 0.65, "Relaxed Evaluation\n(overlap-based\nentity + relation)", C_ORANGE, 7.5, "#333")

    # Arrows from predictions to eval
    _arrow(ax, 3.2, -0.05, 6.7, 0.0, C_GRAY, "->", 1.0)
    _arrow(ax, 10.2, -0.05, 6.7, 0.0, C_GRAY, "->", 1.0)

    # Output
    _box(ax, 6.7, -0.65, 2.2, 0.55, "metrics.json\n+ summary.md", C_GREEN, 8)

    _arrow(ax, 6.7, 0.0, 6.7, -0.35, C_GRAY, "->", 1.0)

    # ═══════════════════════════════════════════════════════════
    # Provider box
    # ═══════════════════════════════════════════════════════════
    _box(ax, 6.7, 5.7, 2.2, 0.75, "LLMClient\nProtocol\n(provider-agnostic)", C_YELLOW, 7.5, "#333")
    _label(ax, 5.4, 5.2, "OpenAI\nor Mock", 6.5)
    _label(ax, 8.0, 5.2, "DeepSeek\nor other", 6.5)

    # Config annotation
    ax.annotate(
        "Config: .env.llm\nLLM_BASE_URL +\nLLM_API_KEY +\nLLM_MODEL",
        xy=(6.7, 5.28), xytext=(0.5, 5.7),
        fontsize=7, ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#F5F5F5", edgecolor=C_GRAY, lw=1),
        zorder=5,
    )

    # ── Legend ──
    legend_items = [
        mpatches.Patch(color=C_BLUE, label="LLM API Call / Strict Eval"),
        mpatches.Patch(color=C_ORANGE, label="Step-wise Decomposition / Relaxed Eval"),
        mpatches.Patch(color=C_PURPLE, label="System Prompt / Schema"),
        mpatches.Patch(color=C_TEAL, label="Postprocessing / Review Step"),
        mpatches.Patch(color=C_GREEN, label="Output Artifacts"),
        mpatches.Patch(color=C_YELLOW, label="Provider Abstraction"),
    ]
    ax.legend(handles=legend_items, loc="upper right", fontsize=7,
              framealpha=0.9, edgecolor="#CCC")

    fig.tight_layout(pad=0.5)
    out = OUTPUT_DIR / "agentic_annotation.png"
    fig.savefig(out, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {out}")


if __name__ == "__main__":
    print("Generating architecture and pipeline diagrams...")
    draw_spert_architecture()
    draw_pipeline_flow()
    draw_agentic_annotation()
    print("Done.")
