#!/usr/bin/env bash
# Download CrowdHuman via Kaggle CLI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:-nkk754/crowdhuman-crowd-human-detection-dataset}"
RAW="$ROOT/data/raw/crowdhuman"
mkdir -p "$RAW"

if [ ! -f "$ROOT/.venv/bin/python" ]; then
  echo "Run bash scripts/setup-train.sh first." >&2
  exit 1
fi

"$ROOT/.venv/bin/python" -m pip install -q kaggle
kaggle datasets download -d "$SLUG" -p "$RAW" --unzip
echo "Next: ./.venv/bin/python scripts/convert_crowdhuman.py"
