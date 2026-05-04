#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/graph}"
cd "$PROJECT_DIR"

export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
export HF_HOME="${HF_HOME:-/root/autodl-tmp/hf_cache}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/root/autodl-tmp/hf_cache}"
export TORCH_HOME="${TORCH_HOME:-/root/autodl-tmp/torch_cache}"
TOKENIZER_PATH="${TOKENIZER_PATH:-microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract}"

mkdir -p outputs/logs outputs/dev100_eval outputs/llm_runs

find_latest_checkpoint() {
  local dataset="$1"
  local label="$2"
  local root="outputs/checkpoints/${dataset}/${label}"

  if [[ ! -d "$root" ]]; then
    echo "Missing checkpoint root: $root" >&2
    return 1
  fi

  find "$root" -mindepth 1 -maxdepth 1 -type d | sort | tail -1
}

find_loadable_model_path() {
  local checkpoint="$1"

  if [[ -f "${checkpoint}/config.json" ]]; then
    echo "$checkpoint"
    return 0
  fi

  local nested
  nested="$(find "$checkpoint" -type f -name config.json | sort | head -1 || true)"
  if [[ -n "$nested" ]]; then
    dirname "$nested"
    return 0
  fi

  echo "No config.json found under checkpoint: $checkpoint" >&2
  find "$checkpoint" -maxdepth 3 -type f | sort | sed -n '1,80p' >&2
  return 1
}

ensure_pytorch_bin() {
  local model_path="$1"
  local bin_path="${model_path}/pytorch_model.bin"
  local safetensors_path="${model_path}/model.safetensors"

  if [[ -f "$bin_path" ]]; then
    return 0
  fi
  if [[ ! -f "$safetensors_path" ]]; then
    echo "Missing both pytorch_model.bin and model.safetensors under: $model_path" >&2
    return 1
  fi

  echo "Converting model.safetensors to pytorch_model.bin under: $model_path"
  MODEL_PATH="$model_path" python - <<'PY'
import os
from pathlib import Path

import torch
from safetensors.torch import load_file

model_path = Path(os.environ["MODEL_PATH"])
state = load_file(model_path / "model.safetensors")
torch.save(state, model_path / "pytorch_model.bin")
print(f"Wrote {model_path / 'pytorch_model.bin'}")
PY
}

ensure_sample() {
  local dataset="$1"
  local raw_path="data/raw/${dataset^^}.json"
  local sample_path="outputs/llm_runs/${dataset}_dev100_sample.json"

  if [[ ! -f "$sample_path" ]]; then
    python scripts/sample_dev_for_llm.py \
      --input "$raw_path" \
      --output "$sample_path" \
      --count 100 \
      --seed 740 >&2
  fi

  echo "$sample_path"
}

make_spert_dev100() {
  local dataset="$1"
  local sample_path="$2"
  local output_dir="outputs/dev100_eval/${dataset}"
  mkdir -p "$output_dir"

  DATASET="$dataset" SAMPLE_PATH="$sample_path" OUTPUT_DIR="$output_dir" python - <<'PY'
import json
import os
from pathlib import Path

dataset = os.environ["DATASET"]
sample_path = Path(os.environ["SAMPLE_PATH"])
output_dir = Path(os.environ["OUTPUT_DIR"])

sample_payload = json.loads(sample_path.read_text(encoding="utf-8"))
sample_ids = {sample["sent_id"] for sample in sample_payload["samples"]}
dev_path = Path("outputs/spert") / dataset / "dev.json"
dev_samples = json.loads(dev_path.read_text(encoding="utf-8"))
selected = [
    sample
    for sample in dev_samples
    if sample.get("orig_id", sample.get("sent_id")) in sample_ids
]

if len(selected) != len(sample_ids):
    found = {sample.get("orig_id", sample.get("sent_id")) for sample in selected}
    missing = sorted(sample_ids - found)
    raise SystemExit(f"Missing {len(missing)} sampled sentences in {dev_path}: {missing[:10]}")

(output_dir / "dev100.json").write_text(json.dumps(selected, indent=2, ensure_ascii=False), encoding="utf-8")
(output_dir / "types.json").write_text((Path("outputs/spert") / dataset / "types.json").read_text(encoding="utf-8"), encoding="utf-8")
import sys
print(f"Wrote {output_dir / 'dev100.json'} with {len(selected)} samples", file=sys.stderr, flush=True)
print(f"Wrote {output_dir / 'types.json'}", file=sys.stderr, flush=True)
PY

  echo "$output_dir/dev100.json"
}

run_eval() {
  local dataset="$1"
  local label="$2"
  local sample_path
  sample_path="$(ensure_sample "$dataset")"
  local eval_data
  eval_data="$(make_spert_dev100 "$dataset" "$sample_path")"
  local checkpoint
  checkpoint="$(find_latest_checkpoint "$dataset" "$label")"
  local model_path
  model_path="$(find_loadable_model_path "$checkpoint")"
  ensure_pytorch_bin "$model_path"

  local out_dir="outputs/dev100_eval/${dataset}/predictions"
  local log_file="outputs/logs/${dataset}_dev100_eval.log"
  mkdir -p "$out_dir"

  if [[ ! -f "outputs/dev100_eval/${dataset}/types.json" ]]; then
    echo "Missing generated types file: outputs/dev100_eval/${dataset}/types.json" >&2
    find "outputs/dev100_eval/${dataset}" -maxdepth 2 -type f | sort >&2 || true
    exit 1
  fi

  echo "=== ${dataset^^} dev100 evaluation ===" | tee "$log_file"
  echo "Sample: $sample_path" | tee -a "$log_file"
  echo "Eval data: $eval_data" | tee -a "$log_file"
  echo "Checkpoint: $checkpoint" | tee -a "$log_file"
  echo "Model path: $model_path" | tee -a "$log_file"
  echo "Tokenizer: $TOKENIZER_PATH" | tee -a "$log_file"

  python external/spert/spert.py eval \
    --dataset_path "$eval_data" \
    --types_path "outputs/dev100_eval/${dataset}/types.json" \
    --model_path "$model_path" \
    --tokenizer_path "$TOKENIZER_PATH" \
    --log_path outputs/logs \
    --label "${dataset}_dev100_eval" \
    --eval_batch_size 4 \
    --max_span_size 10 \
    --rel_filter_threshold 0.4 \
    --max_pairs 100 \
    --store_predictions \
    --predictions_path "$out_dir" 2>&1 | tee -a "$log_file"

  if grep -Eq "Traceback|TypeError|Exception|Error:" "$log_file"; then
    echo "Detected evaluation error in $log_file" >&2
    exit 1
  fi

  echo "Wrote log: $log_file" | tee -a "$log_file"
  echo "Prediction/eval artifacts, if emitted by SpERT, are under: $out_dir" | tee -a "$log_file"
}

run_eval adkg adkg_pubmedbert_e20_bs2
run_eval mdkg mdkg_pubmedbert_e20_bs2
