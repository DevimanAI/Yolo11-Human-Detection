#!/usr/bin/env bash
# Create/reuse .venv and install training dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found." >&2
  exit 1
fi

if [ ! -f "$ROOT/.venv/bin/python" ]; then
  bash "$ROOT/scripts/setup.sh"
fi

"$ROOT/.venv/bin/python" -m pip install --upgrade pip
"$ROOT/.venv/bin/python" -m pip install -r "$ROOT/requirements-train.txt"

"$ROOT/.venv/bin/python" -c "
import torch
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
"

echo "Training environment ready."
echo "  bash scripts/download_dataset.sh"
echo "  ./.venv/bin/python scripts/convert_crowdhuman.py"
echo "  bash scripts/train_yolo11.sh"
