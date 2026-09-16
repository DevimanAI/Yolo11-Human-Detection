#!/usr/bin/env bash
# Create a project venv and install core dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python 3.10+ and retry." >&2
  exit 1
fi

echo "Creating .venv..."
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r "$ROOT/requirements.txt"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Setup complete."
echo "  ./.venv/bin/python scripts/smoke_test.py"
echo "  ./.venv/bin/python run.py"
echo "Optional face recognition:"
echo "  ./.venv/bin/python -m pip install -r requirements-face.txt"
