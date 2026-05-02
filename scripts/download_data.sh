#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-data/raw}"
FOLDER_URL="https://drive.google.com/drive/folders/1AqihJVtS9ZEjZuiESYmAb_ENfL9MTV10?usp=sharing"

mkdir -p "$OUT_DIR"

if ! command -v gdown >/dev/null 2>&1; then
  echo "gdown is required. Install with: conda install -c conda-forge gdown"
  echo "Then run: bash scripts/download_data.sh"
  exit 1
fi

echo "Downloading from: $FOLDER_URL"
echo "Output directory: $OUT_DIR"
gdown --folder "$FOLDER_URL" -O "$OUT_DIR" --remaining-ok

echo
echo "Expected files:"
echo "  $OUT_DIR/ADKG.json"
echo "  $OUT_DIR/MDKG.json"

