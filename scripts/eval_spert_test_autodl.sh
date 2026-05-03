#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/graph}"
cd "$PROJECT_DIR"

export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
export HF_HOME="${HF_HOME:-/root/autodl-tmp/hf_cache}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/root/autodl-tmp/hf_cache}"
export TORCH_HOME="${TORCH_HOME:-/root/autodl-tmp/torch_cache}"
TOKENIZER_PATH="${TOKENIZER_PATH:-microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract}"

mkdir -p outputs/logs outputs/test_eval

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
  echo "Checkpoint contents:" >&2
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

run_eval() {
  local dataset="$1"
  local label="$2"
  local checkpoint
  checkpoint="$(find_latest_checkpoint "$dataset" "$label")"
  local model_path
  model_path="$(find_loadable_model_path "$checkpoint")"
  ensure_pytorch_bin "$model_path"

  local data_dir="outputs/spert/${dataset}"
  local out_dir="outputs/test_eval/${dataset}"
  local log_file="outputs/logs/${dataset}_test_eval.log"
  mkdir -p "$out_dir"

  echo "=== ${dataset^^} test evaluation ===" | tee "$log_file"
  echo "Checkpoint: $checkpoint" | tee -a "$log_file"
  echo "Model path: $model_path" | tee -a "$log_file"
  echo "Tokenizer: $TOKENIZER_PATH" | tee -a "$log_file"
  echo "Test data: ${data_dir}/test.json" | tee -a "$log_file"

  python external/spert/spert.py eval \
    --dataset_path "${data_dir}/test.json" \
    --types_path "${data_dir}/types.json" \
    --model_path "$model_path" \
    --tokenizer_path "$TOKENIZER_PATH" \
    --log_path outputs/logs \
    --label "${dataset}_test_eval" \
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
