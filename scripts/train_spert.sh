#!/usr/bin/env bash
set -euo pipefail

SPERT_DIR="${SPERT_DIR:-external/spert}"
CONFIG="${1:-outputs/spert_configs/adkg.conf}"

if [ ! -d "$SPERT_DIR" ]; then
  echo "SpERT repository not found at $SPERT_DIR"
  echo "Clone it with: git clone https://github.com/lavis-nlp/spert.git $SPERT_DIR"
  exit 1
fi

python "$SPERT_DIR/spert.py" train --config "$CONFIG"

