#!/usr/bin/env bash
set -euo pipefail

echo "== Install deps =="
python -m pip install -r requirements.txt

echo "== Ruff lint =="
ruff check src tests || true

echo "== Pylint duplicate-code =="
pylint --enable=duplicate-code --disable=R,C src || true

echo "== Mypy type check =="
mypy src || true

echo "== Bandit security =="
bandit -q -r src || true

echo "== Radon complexity =="
radon cc -s -a src || true

echo "== Pytest =="
pytest -q

echo "== Done =="
