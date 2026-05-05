#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/graph}"
cd "$PROJECT_DIR"

export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
export HF_HOME="${HF_HOME:-/root/autodl-tmp/hf_cache}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/root/autodl-tmp/hf_cache}"
export TORCH_HOME="${TORCH_HOME:-/root/autodl-tmp/torch_cache}"

TOKENIZER_PATH="${TOKENIZER_PATH:-microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract}"
TARGET_RATIO="${TARGET_RATIO:-0.25}"
TARGET_PCT="${TARGET_PCT:-25}"
SEED="${SEED:-740}"
SOURCE_EPOCHS="${SOURCE_EPOCHS:-8}"
TARGET_EPOCHS="${TARGET_EPOCHS:-8}"
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-2}"
EVAL_BATCH_SIZE="${EVAL_BATCH_SIZE:-4}"
MAX_SPAN_SIZE="${MAX_SPAN_SIZE:-10}"
REL_FILTER_THRESHOLD="${REL_FILTER_THRESHOLD:-0.4}"
MAX_PAIRS="${MAX_PAIRS:-100}"
NEG_ENTITY_COUNT="${NEG_ENTITY_COUNT:-100}"
NEG_RELATION_COUNT="${NEG_RELATION_COUNT:-100}"

mkdir -p outputs/checkpoints/extension_b_low_resource outputs/logs outputs/final_summary

python scripts/make_shared_schema_spert.py \
  --output-dir outputs/spert_shared \
  --target-ratio "$TARGET_RATIO" \
  --seed "$SEED"

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

find_latest_checkpoint() {
  local label="$1"
  local root="outputs/checkpoints/extension_b_low_resource/${label}"

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

train_model() {
  local label="$1"
  local train_path="$2"
  local valid_path="$3"
  local types_path="$4"
  local model_path="$5"
  local epochs="$6"
  local log_file="outputs/logs/${label}.log"

  echo "=== Training ${label} ===" | tee "$log_file"
  echo "Train: $train_path" | tee -a "$log_file"
  echo "Valid: $valid_path" | tee -a "$log_file"
  echo "Model init: $model_path" | tee -a "$log_file"
  echo "Epochs: $epochs" | tee -a "$log_file"

  python external/spert/spert.py train \
    --train_path "$train_path" \
    --valid_path "$valid_path" \
    --types_path "$types_path" \
    --model_path "$model_path" \
    --tokenizer_path "$TOKENIZER_PATH" \
    --save_path outputs/checkpoints/extension_b_low_resource \
    --log_path outputs/logs \
    --label "$label" \
    --epochs "$epochs" \
    --train_batch_size "$TRAIN_BATCH_SIZE" \
    --eval_batch_size "$EVAL_BATCH_SIZE" \
    --max_span_size "$MAX_SPAN_SIZE" \
    --rel_filter_threshold "$REL_FILTER_THRESHOLD" \
    --max_pairs "$MAX_PAIRS" \
    --neg_entity_count "$NEG_ENTITY_COUNT" \
    --neg_relation_count "$NEG_RELATION_COUNT" \
    --store_predictions 2>&1 | tee -a "$log_file"

  if grep -Eq "Traceback|TypeError|Exception|Error:" "$log_file"; then
    echo "Detected training error in $log_file" >&2
    exit 1
  fi
}

eval_model() {
  local run_name="$1"
  local dataset="$2"
  local split="$3"
  local checkpoint_label="$4"
  local checkpoint
  checkpoint="$(find_latest_checkpoint "$checkpoint_label")"
  local model_path
  model_path="$(find_loadable_model_path "$checkpoint")"
  ensure_pytorch_bin "$model_path"

  local out_dir="outputs/extension_b_low_resource_eval/${run_name}/${split}"
  local log_file="outputs/logs/${run_name}_${split}_eval.log"
  mkdir -p "$out_dir"

  echo "=== Eval ${run_name} on ${dataset} ${split} ===" | tee "$log_file"
  echo "Checkpoint: $checkpoint" | tee -a "$log_file"
  echo "Model path: $model_path" | tee -a "$log_file"

  python external/spert/spert.py eval \
    --dataset_path "outputs/spert_shared/${dataset}/${split}.json" \
    --types_path "outputs/spert_shared/${dataset}/types.json" \
    --model_path "$model_path" \
    --tokenizer_path "$TOKENIZER_PATH" \
    --log_path outputs/logs \
    --label "${run_name}_${split}_eval" \
    --eval_batch_size "$EVAL_BATCH_SIZE" \
    --max_span_size "$MAX_SPAN_SIZE" \
    --rel_filter_threshold "$REL_FILTER_THRESHOLD" \
    --max_pairs "$MAX_PAIRS" \
    --store_predictions \
    --predictions_path "$out_dir" 2>&1 | tee -a "$log_file"

  if grep -Eq "Traceback|TypeError|Exception|Error:" "$log_file"; then
    echo "Detected evaluation error in $log_file" >&2
    exit 1
  fi
}

PUBMEDBERT="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"

ADKG_SOURCE_LABEL="extb_source_adkg_full_e${SOURCE_EPOCHS}"
MDKG_SOURCE_LABEL="extb_source_mdkg_full_e${SOURCE_EPOCHS}"
ADKG_BASELINE_LABEL="extb_adkg${TARGET_PCT}_baseline_e${TARGET_EPOCHS}"
MDKG_BASELINE_LABEL="extb_mdkg${TARGET_PCT}_baseline_e${TARGET_EPOCHS}"
ADKG_TO_MDKG_LABEL="extb_adkg_to_mdkg${TARGET_PCT}_e${TARGET_EPOCHS}"
MDKG_TO_ADKG_LABEL="extb_mdkg_to_adkg${TARGET_PCT}_e${TARGET_EPOCHS}"

train_model "$ADKG_SOURCE_LABEL" \
  outputs/spert_shared/adkg/train.json \
  outputs/spert_shared/adkg/dev.json \
  outputs/spert_shared/adkg/types.json \
  "$PUBMEDBERT" \
  "$SOURCE_EPOCHS"

train_model "$MDKG_SOURCE_LABEL" \
  outputs/spert_shared/mdkg/train.json \
  outputs/spert_shared/mdkg/dev.json \
  outputs/spert_shared/mdkg/types.json \
  "$PUBMEDBERT" \
  "$SOURCE_EPOCHS"

ADKG_SOURCE_CKPT="$(find_loadable_model_path "$(find_latest_checkpoint "$ADKG_SOURCE_LABEL")")"
MDKG_SOURCE_CKPT="$(find_loadable_model_path "$(find_latest_checkpoint "$MDKG_SOURCE_LABEL")")"
ensure_pytorch_bin "$ADKG_SOURCE_CKPT"
ensure_pytorch_bin "$MDKG_SOURCE_CKPT"

train_model "$MDKG_BASELINE_LABEL" \
  "outputs/spert_shared/mdkg/train_${TARGET_PCT}.json" \
  outputs/spert_shared/mdkg/dev.json \
  outputs/spert_shared/mdkg/types.json \
  "$PUBMEDBERT" \
  "$TARGET_EPOCHS"

train_model "$ADKG_TO_MDKG_LABEL" \
  "outputs/spert_shared/mdkg/train_${TARGET_PCT}.json" \
  outputs/spert_shared/mdkg/dev.json \
  outputs/spert_shared/mdkg/types.json \
  "$ADKG_SOURCE_CKPT" \
  "$TARGET_EPOCHS"

train_model "$ADKG_BASELINE_LABEL" \
  "outputs/spert_shared/adkg/train_${TARGET_PCT}.json" \
  outputs/spert_shared/adkg/dev.json \
  outputs/spert_shared/adkg/types.json \
  "$PUBMEDBERT" \
  "$TARGET_EPOCHS"

train_model "$MDKG_TO_ADKG_LABEL" \
  "outputs/spert_shared/adkg/train_${TARGET_PCT}.json" \
  outputs/spert_shared/adkg/dev.json \
  outputs/spert_shared/adkg/types.json \
  "$MDKG_SOURCE_CKPT" \
  "$TARGET_EPOCHS"

eval_model "mdkg25_baseline" mdkg dev "$MDKG_BASELINE_LABEL"
eval_model "mdkg25_baseline" mdkg test "$MDKG_BASELINE_LABEL"
eval_model "adkg_to_mdkg25_transfer" mdkg dev "$ADKG_TO_MDKG_LABEL"
eval_model "adkg_to_mdkg25_transfer" mdkg test "$ADKG_TO_MDKG_LABEL"
eval_model "adkg25_baseline" adkg dev "$ADKG_BASELINE_LABEL"
eval_model "adkg25_baseline" adkg test "$ADKG_BASELINE_LABEL"
eval_model "mdkg_to_adkg25_transfer" adkg dev "$MDKG_TO_ADKG_LABEL"
eval_model "mdkg_to_adkg25_transfer" adkg test "$MDKG_TO_ADKG_LABEL"

python scripts/summarize_extension_b_transfer.py \
  --output-dir outputs/final_summary \
  --runs-json outputs/final_summary/extension_b_low_resource_runs.json
