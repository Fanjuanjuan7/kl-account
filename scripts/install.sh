#!/usr/bin/env bash
set -euo pipefail

PY=${PYTHON:-python3}
${PY} -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

python -m playwright install chromium || true
echo "installed. activate with: source .venv/bin/activate"
