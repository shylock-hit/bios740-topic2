# Demo Console Handoff Manual

This document explains the safe operating order for the Extension C demo console so the next user can run it without common path, cache, or stale-process errors.

## Scope

The demo console covers:

- sampling ADKG / MDKG dev examples for LLM annotation
- probing the configured LLM provider
- launching one-shot / workflow experiments
- generating summary tables
- generating artifact charts
- generating error analysis markdown

The frontend is built from `web/` and served by the FastAPI backend in `src/bios740_topic2/demo_api.py`.

## Files You Actually Use

- Backend app: `src/bios740_topic2/demo_api.py`
- Frontend app: `web/src/App.jsx`
- Frontend i18n: `web/src/i18n.js`
- Sampling script: `scripts/sample_dev_for_llm.py`
- Experiment runner: `scripts/run_llm_annotation_experiment.py`
- Summary generator: `scripts/summarize_llm_results.py`
- Artifact generator: `scripts/generate_llm_artifacts.py`
- Error analysis: `scripts/analyze_llm_errors.py`

## First-Time Startup

### 1. Enter the project root

```bash
cd /Users/Zhuanz1/Desktop/graph
```

### 2. Build the frontend before serving it

Do this whenever `web/src/*` changes.

```bash
cd web
npm run build
cd ..
```

### 3. Start the backend

The backend also serves the built frontend.

```bash
PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 127.0.0.1 --port 8010
```

Open:

```text
http://127.0.0.1:8010
```

## Required Restart Rule

If you changed any of the following, restart the backend before using the page:

- `src/bios740_topic2/demo_api.py`
- any Python script under `scripts/`
- any frontend code under `web/src/`

Why:

- Python process memory may still point to old script paths
- the frontend page may still be serving an old built bundle

Typical stale-process symptom:

```json
{
  "detail": "python: can't open file '/Users/.../scripts/sample_adkg_dev_for_llm.py'"
}
```

This means the backend is still running old code. The fix is:

1. stop the old `uvicorn` process
2. rebuild frontend if needed
3. start `uvicorn` again

## Safe Operating Order

Use this order in the UI every time.

### A. Select dataset template

Choose one of:

- `ADKG`
- `MDKG`
- `Custom`

Template behavior:

- `ADKG` fills ADKG defaults
- `MDKG` fills MDKG defaults
- `Custom` leaves fields editable without template overwrite

Current default sample sizes:

- `ADKG`: `100`
- `MDKG`: `30`

### B. Confirm key paths

Before running anything, verify:

- `Raw Input`
- `Sample File`
- `Run Directory`
- `Gold Path`
- `Env File`

For MDKG, expected examples are:

- `data/raw/MDKG.json`
- `outputs/llm_runs/mdkg_dev30_sample.json`
- `mdkg_dev30_deepseek`

### C. Probe provider first

Click:

- `Probe Provider`

Do this before sampling or running experiments.

Reason:

- catches bad API key / bad base URL / protocol mismatch early

### D. Generate sample

Click:

- `Sample Data`

This uses:

- `scripts/sample_dev_for_llm.py`

The script is dataset-agnostic. It works for both ADKG and MDKG as long as the input JSON has `train/dev/test`.

### E. Run experiment

Click:

- `Run Experiment`

Recommended:

- use `both` mode unless debugging only one stage

### F. Wait for both stages to finish

Check the `Live Status` panels:

- `One-shot`
- `Workflow`

Do not generate summary/artifacts/errors before the run completes.

Completion signal:

- progress reaches `processed = total`
- `metrics.json` appears in the run directory

### G. Generate post-run outputs

After the experiment finishes, run these in the UI:

1. `Generate Summary`
2. `Generate Artifacts`
3. `Analyze Errors`

This produces:

- `summary.md`
- `artifacts/`
- error summary markdown

## Output Locations

For a run like `adkg_dev100_deepseek`, outputs are under:

```text
outputs/llm_runs/adkg_dev100_deepseek/
```

Important files:

- `metrics.json`
- `summary.md`
- `one_shot_predictions.json`
- `workflow_predictions.json`
- `one_shot_progress.json`
- `workflow_progress.json`
- `one_shot_progress.jsonl`
- `workflow_progress.jsonl`
- `one_shot_error_summary.md`
- `workflow_error_summary.md`
- `artifacts/artifact_index.md`

## Recommended MDKG Run Strategy

Do not start with `100` samples.

Recommended progression:

1. smoke check: `10`
2. quick comparison: `20` or `30`
3. larger run only if needed: `50`

Reason:

- ADKG `100` samples already took about 90 minutes
- MDKG baseline is stronger, so a smaller LLM sample may already be enough for report discussion

## Common Failure Cases

### 1. Old script path error

Symptom:

```json
{
  "detail": "python: can't open file '/Users/.../scripts/sample_adkg_dev_for_llm.py'"
}
```

Cause:

- old backend process still running

Fix:

- restart `uvicorn`

### 2. Page looks old after frontend edits

Cause:

- `web/dist` not rebuilt

Fix:

```bash
cd web
npm run build
cd ..
PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 127.0.0.1 --port 8010
```

### 3. Summary/artifact generation fails

Check:

- experiment is actually complete
- `metrics.json` exists
- run directory name matches the selected dataset

### 4. Error analysis uses wrong gold file

Cause:

- `Gold Path` still points to ADKG while running MDKG

Fix:

- verify `Gold Path` before clicking `Analyze Errors`

## Minimal Handoff Checklist

Before handing to the next person:

1. note the active dataset
2. note the run directory
3. confirm whether frontend was rebuilt
4. confirm whether backend was restarted after code changes
5. confirm whether `metrics.json`, `summary.md`, and `artifacts/artifact_index.md` exist

## One-Line Rule

If anything about scripts or frontend changed, rebuild `web`, restart `uvicorn`, then use the UI in this order:

`Probe -> Sample -> Run -> Summary -> Artifacts -> Errors`
