#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/graph}"
cd "$PROJECT_DIR"

export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
export HF_HOME="${HF_HOME:-/root/autodl-tmp/hf_cache}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/root/autodl-tmp/hf_cache}"
export TORCH_HOME="${TORCH_HOME:-/root/autodl-tmp/torch_cache}"

mkdir -p outputs/checkpoints/mdkg outputs/logs

python external/spert/spert.py train \
  --train_path outputs/spert/mdkg/train.json \
  --valid_path outputs/spert/mdkg/dev.json \
  --types_path outputs/spert/mdkg/types.json \
  --model_path microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract \
  --tokenizer_path microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract \
  --save_path outputs/checkpoints/mdkg \
  --log_path outputs/logs \
  --label mdkg_pubmedbert_e20_bs2 \
  --epochs 20 \
  --train_batch_size 2 \
  --eval_batch_size 4 \
  --max_span_size 10 \
  --rel_filter_threshold 0.4 \
  --max_pairs 100 \
  --neg_entity_count 100 \
  --neg_relation_count 100 \
  --store_predictions

