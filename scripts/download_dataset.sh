#!/usr/bin/env bash
# Download CrowdHuman subset (default) or full archive with second arg "full".
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SLUG="${1:-leducnhuan/crowdhuman}"
MODE="${2:-subset}"

if [ ! -f "$ROOT/.venv/bin/python" ]; then
  echo "Run bash scripts/setup-train.sh first." >&2
  exit 1
fi

ARGS=( "$ROOT/scripts/download_crowdhuman_subset.py" "--slug" "$SLUG" )
if [ "$MODE" = "full" ]; then
  ARGS+=( "--full" )
fi

"$ROOT/.venv/bin/python" "${ARGS[@]}"
echo "Next: ./.venv/bin/python scripts/convert_crowdhuman.py"
