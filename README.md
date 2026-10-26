# MAS — multi-agent coding workflow template

A lean **plan → code** loop for Claude Code, trimmed down to exactly two
subagents with **fixed models** (no difficulty routing, no model
escalation). One coordinator command drives both, runs verification itself,
and tracks run state on disk so it survives interruptions (including rate
limits).

```
planner (investigates + plans)  ->  coder (implements)
         opus                              sonnet
```

## What's in here

```
.claude/
  agents/
    planner.md     # investigates the codebase itself, writes an exact step-by-step plan — never edits code. Fixed: opus
    coder.md       # implements the plan literally — fixed: sonnet, never escalated
  commands/
    code-task.md   # the coordinator: /code-task — fixed planner->coder route, owns state.json, verifies itself
  statusline.sh    # optional: shows "agent | attempt N | failures N/2"
CLAUDE.md.template  # drop-in CLAUDE.md with the generic workflow + model-policy
                    # sections, and placeholders for this project's own commands/conventions
Artifacts/
  TASK.md.template  # skeleton for the task you hand to /code-task
  .gitkeep
findings/
  README.md         # convention for durable write-ups (not auto-written by any agent)
  .gitkeep
gitignore.snippet    # optional block if you want this kept out of the project's git history
```

These agent/command files are project-agnostic — copy them verbatim. The
only thing to fill in per-project is `CLAUDE.md`.

## Setting up a new project

1. Copy `.claude/` (whole directory) into the new project's root.
2. Copy `CLAUDE.md.template` to the project root as `CLAUDE.md`, and fill in
   `## Project`, `## Commands`, `## Conventions` at the top. Leave
   `## Multi-agent workflow` and `### Model policy` untouched — they're the
   reusable contract the agents/coordinator are written against. If the
   project already has a `CLAUDE.md`, append those two sections to it
   instead of overwriting.
3. Create `Artifacts/` and `findings/` at the project root (copy the
   `.gitkeep`s, or just `mkdir`).
4. Decide whether this tooling is local-only or shared with collaborators:
   - Local-only: append `gitignore.snippet` to the project's `.gitignore`.
   - Shared: commit `.claude/`, `CLAUDE.md`, and `Artifacts/` as-is.
5. If using the statusline, point Claude Code's settings at
   `.claude/statusline.sh` (it degrades to an empty line if `jq` is missing
   or no run has started yet).

## Running it

1. Copy `Artifacts/TASK.md.template` to `Artifacts/TASK.md`, fill in `#
   Task` and `# Notes` (no difficulty field — the two agents' models are
   fixed regardless of task size).
2. Run `/code-task`.
3. The coordinator reads `Artifacts/TASK.md`, invokes `planner` then
   `coder`, verifies the result itself, and reports back what changed, the
   verification result, and where the durable record
   (`Artifacts/state.json`, `Artifacts/dev-diary.md`) landed.

## Design notes worth keeping in mind

- **Each agent has exactly one fixed model, no escalation path.** Planner is
  always Opus, coder is always Sonnet — on a fresh run or a retry. If the
  coder struggles, the fix is a better plan from the planner, never a bigger
  model for the coder.
- **No analyzer, no tester.** The planner investigates the codebase itself
  before writing the plan; the coordinator (or the coder, as part of
  implementing) runs verification directly with Bash instead of a third
  agent.
- **`Artifacts/` vs `findings/`**: `Artifacts/` is per-run and disposable
  (gitignored in the source project) — `state.json` gets overwritten every
  task. `findings/` is cumulative and durable — write-ups that should
  survive long after the task that produced them is forgotten.
- **Two consecutive verification failures stop the loop** rather than
  retrying forever — the coordinator reports and asks, it doesn't grind.
