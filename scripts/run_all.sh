#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${DATA_DIR:-data/raw}"

python scripts/eda.py --input "$DATA_DIR/ADKG.json" --name ADKG
python scripts/eda.py --input "$DATA_DIR/MDKG.json" --name MDKG
python scripts/convert_to_spert.py --input "$DATA_DIR/ADKG.json" --name ADKG
python scripts/convert_to_spert.py --input "$DATA_DIR/MDKG.json" --name MDKG
python scripts/make_spert_configs.py

