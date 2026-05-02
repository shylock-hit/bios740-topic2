#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-data/raw_sources}"
mkdir -p "$OUT_DIR"

ADERC_URL="https://zenodo.org/api/records/5770100/files/ADERC.zip/content"
MDIEC_URL="https://zenodo.org/api/records/10960357/files/MDIEC.zip/content"

echo "Downloading ADERC annotation dataset for ADKG..."
curl -L "$ADERC_URL" -o "$OUT_DIR/ADERC.zip"

echo "Downloading MDIEC/MDERC annotation dataset for MDKG..."
curl -L "$MDIEC_URL" -o "$OUT_DIR/MDIEC.zip"

echo "Unpacking archives..."
unzip -oq "$OUT_DIR/ADERC.zip" -d "$OUT_DIR/ADERC"
unzip -oq "$OUT_DIR/MDIEC.zip" -d "$OUT_DIR/MDIEC"

echo
echo "Downloaded public source datasets to:"
echo "  $OUT_DIR/ADERC"
echo "  $OUT_DIR/MDIEC"
echo
echo "Next: inspect the extracted files and convert them to:"
echo "  data/raw/ADKG.json"
echo "  data/raw/MDKG.json"

