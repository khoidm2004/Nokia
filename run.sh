#!/usr/bin/env bash
# Convenience launcher: loads GROQ_API_KEY from .env and runs the CLI.
#
# Specs live under specs/<kind>/*.txt, one subdirectory per kind of spec
# (e.g. specs/sample/, specs/ecommerce/, specs/banking/...) so different
# test specs don't pile up in one flat directory. Outputs mirror the same
# <kind> subdirectory under outputs/, derived automatically from the input
# path unless you pass an explicit output path.
#
#   ./run.sh                                        -> specs/sample/sample_spec.txt -> outputs/sample/model.html
#   ./run.sh specs/sample/sample_spec.txt           -> outputs/sample/model.html (kind = "sample", derived)
#   ./run.sh specs/ecommerce/checkout.txt           -> outputs/ecommerce/model.html (kind = "ecommerce", derived)
#   ./run.sh specs/sample/sample_spec.txt out.html  -> out.html (explicit output always wins)
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

INPUT="${1:-specs/sample/sample_spec.txt}"

if [ -n "${2:-}" ]; then
  OUTPUT="$2"
elif [[ "$INPUT" == specs/* ]]; then
  REL="${INPUT#specs/}"
  KIND="$(dirname "$REL")"
  OUTPUT="outputs/${KIND}/model.html"
else
  OUTPUT="outputs/model.html"
fi

mkdir -p "$(dirname "$OUTPUT")"
.venv/bin/python -m app.main --input "$INPUT" --output "$OUTPUT"
