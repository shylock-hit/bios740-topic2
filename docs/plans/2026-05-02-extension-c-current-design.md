# Extension C Current Design

## Goal

This document captures the current engineering design for Extension C: an LLM-based biomedical
annotation workflow on ADKG development samples. It is a project-internal design note, not report
text.

The current target experiment is:

- Dataset: ADKG
- Split: dev
- Sample size: 100 sentences
- Modes:
  - one-shot extraction
  - 3-step workflow (`extract_entities -> extract_relations -> review_and_fix`)
- Providers:
  - primary: OpenAI-compatible API
  - fallback: DeepSeek-compatible API

## Design Principles

1. Reuse the existing ADKG/MDKG loading and strict evaluation code.
2. Keep provider integration thin and replaceable.
3. Make the workflow runnable without live API access by using a mock client.
4. Produce artifacts that can be dropped directly into later analysis and reporting.
5. Avoid heavy dependencies until the real API path is stable.

## Current Module Layout

### Core LLM extension modules

- `src/bios740_topic2/llm_schema.py`
  - Defines allowed ADKG entity labels and relation labels.
  - Normalizes LLM payloads into a fixed structure:
    - `entities: [{"text": ..., "type": ...}]`
    - `relations: [{"head": ..., "type": ..., "tail": ...}]`
  - Validates labels against the ADKG schema.

- `src/bios740_topic2/llm_postprocess.py`
  - Aligns predicted entity text back to character spans in the source sentence.
  - Builds prediction samples in the same shape expected by the existing evaluator.
  - Links relations by resolved entity text.

- `src/bios740_topic2/relaxed_evaluate.py`
  - Implements overlap-based relaxed metrics.
  - Relaxed entity match: same sentence, same type, overlapping spans.
  - Relaxed relation match: same sentence, same type, overlapping head span, overlapping tail span.

- `src/bios740_topic2/llm_workflow.py`
  - Defines the lightweight workflow abstraction.
  - Supports:
    - `run_one_shot`
    - `run_entities_then_relations`
  - Uses a provider-agnostic `LLMClient` protocol.

- `src/bios740_topic2/llm_client.py`
  - Defines OpenAI-compatible HTTP client support.
  - Loads config from environment variables or `.env`-style file.
  - Builds prompt variants for the four prompt names:
    - `one_shot`
    - `extract_entities`
    - `extract_relations`
    - `review_and_fix`

### Scripts

- `scripts/sample_adkg_dev_for_llm.py`
  - Loads `data/raw/ADKG.json`
  - Samples a deterministic subset from the `dev` split
  - Writes a JSON artifact with metadata and sampled sentences

- `scripts/run_llm_annotation_experiment.py`
  - Loads sampled sentences
  - Runs one-shot mode and/or workflow mode
  - Postprocesses predictions into evaluator-compatible format
  - Computes:
    - strict metrics via `evaluate.py`
    - relaxed metrics via `relaxed_evaluate.py`
  - Writes:
    - `one_shot_predictions.json`
    - `workflow_predictions.json`
    - `metrics.json`

- `scripts/summarize_llm_results.py`
  - Reads `metrics.json`
  - Writes a compact markdown summary table for later use

## Data Flow

The end-to-end flow is:

1. `data/raw/ADKG.json`
2. `sample_adkg_dev_for_llm.py`
3. `outputs/llm_runs/adkg_dev100_sample.json`
4. `run_llm_annotation_experiment.py`
5. provider call(s) through `llm_workflow.py`
6. payload normalization through `llm_schema.py`
7. span alignment through `llm_postprocess.py`
8. strict scoring through `evaluate.py`
9. relaxed scoring through `relaxed_evaluate.py`
10. result summary through `summarize_llm_results.py`

## Current Output Contract

### Sample artifact

The sampled input file has this shape:

```json
{
  "dataset": "ADKG",
  "split": "dev",
  "seed": 740,
  "count": 100,
  "samples": [...]
}
```

### Prediction payload

Internal normalized LLM payload:

```json
{
  "entities": [
    {"text": "APOE", "type": "gene"}
  ],
  "relations": [
    {"head": "APOE", "type": "associated_with", "tail": "dementia"}
  ]
}
```

### Experiment output

Expected output directory contents:

```text
outputs/llm_runs/<run_name>/
  one_shot_predictions.json
  workflow_predictions.json
  metrics.json
  summary.md
```

## Configuration

### Environment file

The runner expects `.env.llm` in the project root by default.

Template file:

- `.env.llm.example`

Current supported keys:

```text
LLM_BASE_URL=...
LLM_API_KEY=...
LLM_MODEL=...
```

Examples:

```text
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-5.2
```

```text
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

## Current Validation Status

The following test coverage exists:

- `tests/test_llm_schema.py`
- `tests/test_llm_postprocess.py`
- `tests/test_llm_sampling.py`
- `tests/test_relaxed_evaluate.py`
- `tests/test_llm_workflow.py`
- `tests/test_llm_client.py`

Verified locally:

- 12 LLM-extension tests pass
- sample generation works
- mock workflow run works
- metrics summary generation works

## Known Gap

The code path for real API execution is implemented, but the current run has not succeeded because
the configured `LLM_BASE_URL` in `.env.llm` could not be resolved by the local environment.

Observed failure class:

- URL resolution / host lookup failure before the request reached the provider

This indicates a configuration or network issue, not a workflow-logic issue.

## Immediate Next Step

After fixing `.env.llm`, the next command to run is:

```bash
python scripts/run_llm_annotation_experiment.py \
  --sample outputs/llm_runs/adkg_dev100_sample.json \
  --output-dir outputs/llm_runs/adkg_dev100_gpt \
  --mode both \
  --provider openai_compat \
  --env-file .env.llm
```

Then:

```bash
python scripts/summarize_llm_results.py \
  --metrics outputs/llm_runs/adkg_dev100_gpt/metrics.json \
  --output outputs/llm_runs/adkg_dev100_gpt/summary.md
```

## What This Design Deliberately Does Not Do Yet

- No LangGraph dependency yet
- No asynchronous batching or parallel API execution
- No token/cost accounting yet
- No retry/backoff logic yet
- No provider-specific parsing adapters beyond OpenAI-compatible chat completions
- No direct report integration

These are postponed until the real API path is stable.
