#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/graph}"
cd "$PROJECT_DIR"

export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
export HF_HOME="${HF_HOME:-/root/autodl-tmp/hf_cache}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/root/autodl-tmp/hf_cache}"
export TORCH_HOME="${TORCH_HOME:-/root/autodl-tmp/torch_cache}"

mkdir -p outputs/checkpoints/transfer_shared outputs/logs

python scripts/make_shared_schema_spert.py

python external/spert/spert.py train \
  --train_path outputs/spert_shared/adkg/train.json \
  --valid_path outputs/spert_shared/mdkg/dev.json \
  --types_path outputs/spert_shared/adkg/types.json \
  --model_path microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract \
  --tokenizer_path microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract \
  --save_path outputs/checkpoints/transfer_shared \
  --log_path outputs/logs \
  --label adkg_to_mdkg_shared_source_e10 \
  --epochs 10 \
  --train_batch_size 2 \
  --eval_batch_size 4 \
  --max_span_size 10 \
  --rel_filter_threshold 0.4 \
  --max_pairs 100 \
  --neg_entity_count 100 \
  --neg_relation_count 100 \
  --store_predictions

SOURCE_CKPT="$(find outputs/checkpoints/transfer_shared/adkg_to_mdkg_shared_source_e10 -mindepth 1 -maxdepth 1 -type d | sort | tail -1)"
echo "Using source checkpoint: $SOURCE_CKPT"

python external/spert/spert.py train \
  --train_path outputs/spert_shared/mdkg/train.json \
  --valid_path outputs/spert_shared/mdkg/dev.json \
  --types_path outputs/spert_shared/mdkg/types.json \
  --model_path "$SOURCE_CKPT" \
  --tokenizer_path microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract \
  --save_path outputs/checkpoints/transfer_shared \
  --log_path outputs/logs \
  --label adkg_to_mdkg_shared_finetune_e10 \
  --epochs 10 \
  --train_batch_size 2 \
  --eval_batch_size 4 \
  --max_span_size 10 \
  --rel_filter_threshold 0.4 \
  --max_pairs 100 \
  --neg_entity_count 100 \
  --neg_relation_count 100 \
  --store_predictions
