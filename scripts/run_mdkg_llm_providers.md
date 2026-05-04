# MDKG dev100 GPT/Gemini LLM Runs

This protocol runs MDKG-specific prompts/schema on the same fixed MDKG dev100 sample.

## 1. Prepare Sample

```bash
python scripts/sample_dev_for_llm.py \
  --input data/raw/MDKG.json \
  --output outputs/llm_runs/mdkg_dev100_sample.json \
  --count 100 \
  --seed 740
```

## 2. Probe Providers

Create provider env files outside git tracking:

```bash
cp .env.llm.example .env.gpt
cp .env.llm.example .env.gemini
```

Expected GPT-style env:

```text
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=...
LLM_MODEL=gpt-4o-mini
LLM_WIRE_API=chat_completions
```

Expected Gemini OpenAI-compatible env:

```text
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_API_KEY=...
LLM_MODEL=gemini-1.5-flash
LLM_WIRE_API=chat_completions
```

Probe both with the MDKG schema:

```bash
python scripts/probe_llm_provider.py --env-file .env.gpt --dataset MDKG
python scripts/probe_llm_provider.py --env-file .env.gemini --dataset MDKG
```

## 3. Run MDKG dev100

Run one-shot and workflow in provider-specific unique directories:

```bash
python scripts/run_llm_annotation_experiment.py \
  --sample outputs/llm_runs/mdkg_dev100_sample.json \
  --output-dir outputs/llm_runs/mdkg_dev100_gpt_$(date +%Y%m%d_%H%M%S) \
  --mode both \
  --provider openai_compat \
  --env-file .env.gpt \
  --dataset MDKG
```

```bash
python scripts/run_llm_annotation_experiment.py \
  --sample outputs/llm_runs/mdkg_dev100_sample.json \
  --output-dir outputs/llm_runs/mdkg_dev100_gemini_$(date +%Y%m%d_%H%M%S) \
  --mode both \
  --provider openai_compat \
  --env-file .env.gemini \
  --dataset MDKG
```

Each run writes:

- `metrics.json`
- `one_shot_predictions.json`
- `workflow_predictions.json`
- `one_shot_progress.json/jsonl`
- `workflow_progress.json/jsonl`

## 4. SpERT dev100 Anchor

On AutoDL with trained checkpoints:

```bash
bash scripts/eval_spert_dev100_autodl.sh
```

This evaluates saved ADKG and MDKG SpERT checkpoints on the same fixed dev100 samples used by the LLM runs.
