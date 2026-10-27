# Nokia — Spec to Abstraction Model

Entry for the **Nokia Student Network Challenge 2026**.

A multi-agent CLI that turns a requirements / specification document into a
draft **abstraction model** for software testers: every feature in the
spec, plus how those features relate (dependencies, triggers, shared data,
exclusions, sub-features). The goal is a fast visual first look before a
human writes a test plan — not a verified formal model of the system.

**Input:** one `.txt` requirements/spec file  
**Output:** portable `model.html` (feature list + interactive graph) and a
sibling `model.json`

Full technical design: [`artifacts/Architect.md`](artifacts/Architect.md)

---

## Multi-agent pipeline

Specs are processed by a **LangGraph** workflow: three LLM agents hand off
to each other, with deterministic steps around them for ingest, validation,
and rendering.

```
.txt spec
   │
   ▼
[ingest]                 read, normalize, number lines (traceability)
   │
   ▼
[extract_features]       AGENT — every feature / requirement in the doc
   │
   ▼
[map_relationships]      AGENT — typed edges between features
   │
   ▼
[critique]               AGENT — coverage / edge sanity check
   │                        needs revision? ──yes (max 1×)──▶ extract again
   │no
   ▼
[consistency_check]      drop dangling edges, flag orphans / duplicates
   │
   ▼
[assemble + render]      write model.json + self-contained model.html
```

| Agent | Role |
|---|---|
| **Extractor** | Reads the numbered spec and emits features (`F1…Fn`) with name, description, category, and source line range |
| **Relationship mapper** | Connects features with `depends_on`, `triggers`, `excludes`, `shares_data`, or `part_of`, each with a rationale |
| **Critic** | Reviews the draft; can force one revision pass or attach warnings for the tester |

Relationship types and the interactive graph give testers a map of the
system *from the written requirements*, before they invent test cases.

---

## Quick start

```bash
# setup
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt

# needs GROQ_API_KEY (or put it in .env and use ./run.sh)
export GROQ_API_KEY=gsk_...

# run on the sample FleetLink telematics spec
./run.sh
# or:
.venv/bin/python -m app.main \
  --input samples/sample_spec.txt \
  --output outputs/model.html

# open outputs/model.html in a browser (graph libs load from CDN)
```

```bash
# tests
.venv/bin/python -m pytest -q
```

---

## Project layout

```
app/
  agents/          # extractor, relationship mapper, critic (+ LLM client)
  nodes/           # ingest, consistency_check, assemble, render
  prompts/         # system prompts for each agent
  graph.py         # LangGraph wiring
  main.py          # CLI entrypoint
samples/           # example .txt specs
outputs/           # generated model.html / model.json
artifacts/         # architecture + task notes for agent-assisted builds
```

---

## Scope notes

- Output is an **LLM draft** for a human tester to review — not a verified
  model of the system.
- v1 reads a **single `.txt` file** in one pass (hard size guard; no
  chunking). Oversized specs fail loudly instead of being truncated.
- The tool **stops at the abstraction model**; it does not generate a test
  plan.
- Viewing the HTML graph needs network access (Cytoscape.js via CDN).
