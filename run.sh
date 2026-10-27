#!/usr/bin/env bash
# Convenience launcher: loads GROQ_API_KEY from .env and runs the CLI.
#
#   ./run.sh                                  -> samples/sample_spec.txt -> outputs/model.html
#   ./run.sh my_spec.txt                      -> my_spec.txt -> outputs/model.html
#   ./run.sh my_spec.txt outputs/my_model.html -> my_spec.txt -> outputs/my_model.html
#
# Requires .venv (uv venv --python 3.13 .venv && uv pip install -r requirements.txt)
# and a .env file containing GROQ_API_KEY=... in this directory.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "error: .env not found in $(pwd). Create it with: echo 'GROQ_API_KEY=gsk_...' > .env" >&2
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "error: .venv not found. Run: uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python -r requirements.txt" >&2
  exit 1
fi

export GROQ_API_KEY="$(grep '^GROQ_API_KEY=' .env | head -n1 | cut -d= -f2-)"

INPUT="${1:-samples/sample_spec.txt}"
OUTPUT="${2:-outputs/model.html}"

.venv/bin/python -m app.main --input "$INPUT" --output "$OUTPUT"
