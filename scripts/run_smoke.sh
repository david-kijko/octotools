#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"

export FORGE_API_KEY="${FORGE_API_KEY:-oauth-wrapper}"
export FORGE_API_BASE="${FORGE_API_BASE:-http://127.0.0.1:4141/v1}"

if [[ ! -x "$PYTHON" ]]; then
  echo "Missing venv python at $PYTHON" >&2
  echo "Create it with: uv venv .venv --python 3.12 && uv pip install -r requirements.txt --exclude-package vllm" >&2
  exit 1
fi

cd "$ROOT"

if [[ $# -gt 0 ]]; then
  exec "$PYTHON" "$@"
fi

TASK="${TASK:-mathvista}"
INDEX="${INDEX:-100}"
LLM="${LLM:-forge/gpt-5.4}"
ENABLED_TOOLS="${ENABLED_TOOLS:-Relevant_Patch_Zoomer_Tool,Google_Search_Tool,Python_Code_Generator_Tool,Image_Captioner_Tool,Generalist_Solution_Generator_Tool}"

exec "$PYTHON" tasks/solve.py \
  --index "$INDEX" \
  --task "$TASK" \
  --data_file "tasks/$TASK/data/data.json" \
  --llm_engine_name "$LLM" \
  --root_cache_dir "tasks/$TASK/cache/c1-smoke" \
  --output_json_dir "tasks/$TASK/results/c1-smoke" \
  --output_types direct \
  --enabled_tools "$ENABLED_TOOLS" \
  --max_time 300 \
  --toolbox_mode image
