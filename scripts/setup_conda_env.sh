#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="${1:-bios740-topic2}"

if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  echo "Conda environment '$ENV_NAME' already exists."
else
  conda create -n "$ENV_NAME" python=3.10 -y
fi

conda run -n "$ENV_NAME" python -m pip install --upgrade pip
conda run -n "$ENV_NAME" python -m pip install -e ".[dev]"
conda install -n "$ENV_NAME" -c conda-forge gdown -y || true

echo
echo "Activate with:"
echo "  conda activate $ENV_NAME"
echo
echo "Then download data with:"
echo "  bash scripts/download_data.sh data/raw"
