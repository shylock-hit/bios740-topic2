# LLM Evaluation Enhancements

## Purpose

This note summarizes the recent engineering changes added around the LLM annotation workflow. It is
intended as an internal implementation record for the current diff, not as report text.

The goal of these changes was to increase the analytical value of Extension C by adding:

- visible runtime progress
- better robustness for long-running API experiments
- stronger system-level evaluation outputs
- lightweight error analysis outputs

## What Was Added

### 1. Incremental progress tracking

File:

- `scripts/run_llm_annotation_experiment.py`

New behavior:

- writes progress continuously while the experiment is running
- emits a compact progress snapshot JSON per mode
- emits a JSONL event log per processed sample
- writes predictions incrementally instead of only at the end
- prints progress every 5 samples

Generated files per mode:

```text
<mode>_progress.json
<mode>_progress.jsonl
<mode>_predictions.json
```

Example:

```text
outputs/llm_runs/adkg_dev100_deepseek/one_shot_progress.json
outputs/llm_runs/adkg_dev100_deepseek/one_shot_progress.jsonl
```

This makes the experiment inspectable during execution and avoids the previous “black box until
completion” behavior.

### 2. Expanded system metrics

File:

- `scripts/run_llm_annotation_experiment.py`

New metrics added to `metrics.json`:

- `avg_latency_seconds`
- `p50_latency_seconds`
- `p90_latency_seconds`
- `parse_success_count`
- `parse_success_rate`
- `failure_count`
- `validation_error_count`

These are recorded separately for `one_shot` and `workflow`.

This improves the extension from “accuracy only” into a more complete annotation system evaluation.

### 3. Two-table markdown summary

File:

- `scripts/summarize_llm_results.py`

The summary output now contains two sections:

1. `Quality`
   - strict entity F1
   - strict relation F1
   - relaxed entity F1
   - relaxed relation F1

2. `System`
   - average latency
   - p50 latency
   - p90 latency
   - parse success
   - failures
   - validation errors

This directly supports a stronger report table structure.

### 4. Lightweight error analysis script

File:

- `scripts/analyze_llm_errors.py`

Current outputs:

- count of boundary overlap errors
- failure type histogram from progress JSONL
- up to 10 boundary error examples

Inputs:

- gold sample JSON
- prediction JSON
- optional progress JSONL

Output:

- markdown summary file

This is intended to support the “error analysis” part of the extension without requiring a heavy
manual review workflow.

## Why These Changes Matter

These additions raise the practical value of the extension in four ways:

1. They make long-running API experiments observable while they are still running.
2. They produce system metrics that are meaningful for LLM-based annotation pipelines.
3. They make one-shot vs workflow comparison easier to summarize cleanly.
4. They create a direct path from raw predictions to error-analysis text.

## Files Touched by This Diff

Modified:

- `scripts/run_llm_annotation_experiment.py`
- `scripts/summarize_llm_results.py`
- `scripts/analyze_llm_errors.py`

Related existing files used by the enhanced workflow:

- `src/bios740_topic2/llm_schema.py`
- `src/bios740_topic2/llm_postprocess.py`
- `src/bios740_topic2/relaxed_evaluate.py`
- `src/bios740_topic2/llm_workflow.py`
- `src/bios740_topic2/llm_client.py`

## Current Output Contract

Expected experiment directory:

```text
outputs/llm_runs/<run_name>/
  metrics.json
  summary.md
  error_summary.md
  one_shot_predictions.json
  one_shot_progress.json
  one_shot_progress.jsonl
  workflow_predictions.json
  workflow_progress.json
  workflow_progress.jsonl
```

## Validation Status

The enhanced scripts were validated locally with mock runs:

- progress files are created and updated incrementally
- predictions are written during execution
- summary markdown is generated from `metrics.json`
- error summary markdown is generated from gold/prediction/progress inputs

The mock metrics are not meaningful scientifically; they only confirm the execution path and output
format.

## Remaining Limitation

The real DeepSeek experiment is still the source of the final scientific numbers. The enhancements
improve observability and analysis, but they do not change the underlying model outputs.
