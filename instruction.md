# SModel — user instructions

How to install and run **SModel**. For project background, the multi-agent
pipeline, and design notes, see [`README.md`](README.md).

---

## What you get

You give SModel a plain-text requirements / specification file (`.txt`).
It produces:

| File | Purpose |
|---|---|
| `model.html` | Interactive feature list + relationship graph (open in a browser) |
| `model.json` | Same model as structured data, next to the HTML |

The HTML graph loads Cytoscape.js from a CDN, so viewing it needs network
access.

---

## Requirements

- **Python 3.13**
- **[uv](https://docs.astral.sh/uv/)** (recommended for creating the venv and installing deps)
- A **Groq API key** (`GROQ_API_KEY`) — the pipeline calls Groq for the LLM agents

---

## Installation

From the project root:

```bash
# 1. Create a virtual environment
uv venv --python 3.13 .venv

# 2. Install dependencies
uv pip install --python .venv/bin/python -r requirements.txt

# 3. Put your Groq key in a local .env (used by ./run.sh)
echo 'GROQ_API_KEY=gsk_your_key_here' > .env
```

Do not commit `.env`. You can also export the key in your shell instead of
using `.env` if you call the Python module directly:

```bash
export GROQ_API_KEY=gsk_your_key_here
```

---

## How to use

### Option A — `./run.sh` (easiest)

`./run.sh` loads `GROQ_API_KEY` from `.env` and picks a default output path
under `outputs/` that mirrors `specs/<kind>/`.

```bash
# Sample FleetLink telematics spec → outputs/sample/model.html
./run.sh

# Your own spec under specs/<kind>/
./run.sh specs/ecommerce/checkout.txt
# → outputs/ecommerce/model.html (+ model.json)

# Explicit output path (overrides the default)
./run.sh specs/sample/sample_spec.txt path/to/my_model.html
```

### Option B — Python module

```bash
export GROQ_API_KEY=gsk_...

.venv/bin/python -m app.main \
  --input specs/sample/sample_spec.txt \
  --output outputs/sample/model.html
```

| Flag | Required | Description |
|---|---|---|
| `--input` | yes | Path to the `.txt` spec file |
| `--output` | no | HTML path to write (default: `outputs/model.html`). JSON is written beside it with a `.json` suffix |

### Open the result

Open the generated `model.html` in a browser. You should see a feature
sidebar, an interactive graph, a legend, and any warnings from the critic.

---

## Preparing your own spec

1. Put a `.txt` file under `specs/<kind>/` (create a subdirectory per kind of
   spec, e.g. `specs/sample/`, `specs/ecommerce/`).
2. Prefer roughly **20–25 distinct extractable requirements** per file so
   the LLM responses stay within token limits. Larger or denser docs should
   be split (e.g. by category) and run separately.
3. Run `./run.sh` (or the module) as above and review `outputs/<kind>/`.

More detail on sizing limits and layout: [`README.md`](README.md)
(sections *Specs and outputs* and *Spec sizing limits*).

---

## Tests (optional)

```bash
.venv/bin/python -m pytest -q
```

---

## Common problems

| Symptom | What to check |
|---|---|
| `GROQ_API_KEY is not set` | Export the key, or create `.env` with `GROQ_API_KEY=...` and use `./run.sh` |
| `.env not found` / `.venv not found` | Finish the installation steps above |
| `tool_use_failed` / JSON parse errors from Groq | Spec likely too large or too dense — split into smaller files (see README sizing notes) |
| Graph blank / libs missing | Ensure the browser can reach the CDN (network access) |

---

## Scope reminders

- Output is an **LLM draft** for a human tester — not a verified system model.
- v1 accepts a **single `.txt` file** (no multi-file merge in one run).
- The tool stops at the abstraction model; it does not write a test plan.

Full overview and architecture links: [`README.md`](README.md).
