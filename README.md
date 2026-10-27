# SModel — Spec to Abstraction Model

**SModel** (short for Spec Model) turns a requirements / specification
document into a draft **abstraction model** for software testers: every
feature in the spec, plus how those features relate (dependencies,
triggers, shared data, exclusions, sub-features). The goal is a fast
visual first look before a human writes a test plan — not a verified
formal model of the system.

Entry for the **Nokia Student Network Challenge 2026**.

**Input:** one `.txt` requirements/spec file  
**Output:** portable `model.html` (feature list + interactive graph) and a
sibling `model.json`

**Install & usage:** [`instruction.md`](instruction.md)  
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
  --input specs/sample/sample_spec.txt \
  --output outputs/sample/model.html

# open outputs/sample/model.html in a browser (graph libs load from CDN)
```

```bash
# tests
.venv/bin/python -m pytest -q
```

---

## Specs and outputs

Spec documents live under `specs/<kind>/*.txt`, one subdirectory per kind
of spec (e.g. `specs/sample/`, `specs/ecommerce/`) so different test specs
don't pile up in one flat directory. `./run.sh` mirrors that `<kind>`
subdirectory under `outputs/` automatically — `outputs/sample/model.html`
for `specs/sample/...`, `outputs/ecommerce/model.html` for
`specs/ecommerce/...`, and so on — unless you pass an explicit output path.

### Spec sizing limits

Besides the 40,000-character single-pass guard (below), each LLM agent
returns its *entire* JSON result in one Groq call, bounded by a fixed
output-token budget — currently 8,000 tokens for the extractor
(`app/agents/extractor.py`) and 6,000 for the relationship mapper
(`app/agents/relationship_mapper.py`). A spec with many dozens of distinct
"shall" requirements can exceed that budget mid-generation: the response
gets cut off before its JSON closes, and Groq returns a `tool_use_failed` /
"Failed to parse tool call arguments as JSON" error rather than a usable
(even partial) result.

In practice, keep a single spec file to roughly **20-25 distinct
extractable requirements**. A denser real-world document (we hit this with
a ~60-requirement mechanical-engineering spec) should be split into
several smaller files — e.g. one per requirement category — each run
separately rather than widened against a single over-budget call.

The two budgets interact: the relationship mapper's 6,000-token limit is
driven by how many *edges* the feature set implies, not just the feature
count. Merging two specs that describe the same system (e.g. a
requirements doc and a specifications doc for the same equipment) produces
far more cross-references per feature than two unrelated specs of the same
size — a merged 24-feature document blew the relationship mapper's budget
where two separate 20-feature documents on different topics didn't. If
you're combining overlapping documents into one spec, aim lower than
20-25 items (we landed on 17 for a merged requirements+specifications
doc) rather than just summing each document's safe item count.

## Project layout

```
app/
  agents/          # extractor, relationship mapper, critic (+ LLM client)
  nodes/           # ingest, consistency_check, assemble, render
  prompts/         # system prompts for each agent
  graph.py         # LangGraph wiring
  main.py          # CLI entrypoint
specs/<kind>/      # example .txt specs, one subdirectory per kind
outputs/<kind>/    # generated model.html / model.json, mirrors specs/<kind>/
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
