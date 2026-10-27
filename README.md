# Nokia — Spec to Abstraction Model

A Python/LangGraph multi-agent CLI tool that turns a requirements/spec
document (`.txt` in v1) into a self-contained HTML "abstraction model" for
a software tester: a list of every feature in the doc, plus a graph of how
those features relate to each other (dependencies, triggers, shared state,
exclusions, sub-features) — giving the tester a visual first look before
writing a test plan. See `artifacts/Architect.md` for the full approved
technical design.

## Commands

```
# setup
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt

# run (needs GROQ_API_KEY)
export GROQ_API_KEY=gsk_...
.venv/bin/python -m app.main --input samples/sample_spec.txt --output outputs/sample_model.html

# test
.venv/bin/python -m pytest -q
```

## Limitations

- The output is a draft model produced by an LLM reading the spec. It is a
  starting point for a human tester to review, not a verified model of the
  system.
- v1 only reads a single `.txt` file in one pass: there is a hard
  40,000-character guard (`MAX_SPEC_CHARS` in `app/nodes/ingest.py`) and no
  chunking, so oversized specs fail loudly instead of being silently
  truncated.
- The tool stops at the abstraction model; it does not generate a test
  plan.

The generated HTML loads Cytoscape.js, dagre and cytoscape-dagre from a CDN
(unpkg.com), so an internet connection is required to view the graph in a
browser.
