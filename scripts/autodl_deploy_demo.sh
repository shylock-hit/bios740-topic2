#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/autodl-tmp/graph}"
ENV_NAME="${1:-bios740-topic2}"
PORT="${PORT:-6008}"

echo "[1/5] Enter project directory"
cd "$PROJECT_DIR"

echo "[2/5] Ensure conda environment exists and Python deps are installed"
bash scripts/setup_conda_env.sh "$ENV_NAME"

echo "[3/5] Install frontend dependencies"
cd web
npm install

echo "[4/5] Build frontend"
npm run build
cd "$PROJECT_DIR"

echo "[5/5] Deployment preparation complete"
echo
echo "Next steps:"
echo "  1. conda activate $ENV_NAME"
echo "  2. cp .env.llm.example .env.llm"
echo "  3. edit .env.llm and fill LLM_API_KEY if you plan to run live LLM experiments"
echo "  4. start the demo server:"
echo
echo "     PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 0.0.0.0 --port $PORT"
echo
echo "Background mode:"
echo
echo "     nohup env PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 0.0.0.0 --port $PORT > outputs/logs/demo_console.log 2>&1 &"
echo
echo "Then use AutoDL custom service to expose port $PORT and open the mapped URL in your browser."
echo "If your account cannot expose the port directly, use an SSH tunnel instead."
