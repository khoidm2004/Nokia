# MAS — multi-agent coding workflow template

A lean **plan → code** loop for Claude Code, trimmed down to exactly two
subagents with **fixed models** (no difficulty routing, no model
escalation). One coordinator command drives both, runs verification itself,
commits and merges finished work into `main` on its own, and tracks run
state on disk so it survives interruptions (including rate limits).

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
    code-task.md   # the coordinator: /code-task — fixed planner->coder route, owns git + state.json, verifies itself
  statusline.sh    # optional: shows "agent | attempt N | failures N/2"
CLAUDE.md            # project commands/conventions + the multi-agent workflow contract
CONTRIBUTING.md      # commit message convention (Conventional Commits) the coordinator commits with
artifacts/
  TASK.md           # the task you hand to /code-task — edit `# Task` / `# Notes` and run it
  .gitkeep
findings/
  README.md         # convention for durable write-ups (not auto-written by any agent)
  .gitkeep
```

## Running it

1. Edit `artifacts/TASK.md` — fill in `# Task` and `# Notes` (no difficulty
   field — the two agents' models are fixed regardless of task size).
2. Run `/code-task`.
3. The coordinator creates a `task/<slug>` branch off `main`, invokes
   `planner` then `coder` on it, verifies the result itself, and — once it
   passes (or finishes unverified, if `CLAUDE.md` has no check commands
   yet) — commits the changed files and merges that branch into `main`
   itself (`--ff-only` when possible, `--no-ff` otherwise; it never pushes
   to a remote). It reports back what changed, the verification result, and
   whether/where it landed on `main`.

## Design notes worth keeping in mind

- **Each agent has exactly one fixed model, no escalation path.** Planner is
  always Opus, coder is always Sonnet — on a fresh run or a retry. If the
  coder struggles, the fix is a better plan from the planner, never a bigger
  model for the coder.
- **No analyzer, no tester.** The planner investigates the codebase itself
  before writing the plan; the coordinator (or the coder, as part of
  implementing) runs verification directly with Bash instead of a third
  agent.
- **The coordinator commits and merges, you never have to.** Every run gets
  its own branch so `main` only ever holds delivered work. A merge conflict
  stops the loop (`git merge --abort`, branch left intact) rather than
  being resolved automatically, and nothing is ever pushed to a remote
  without you asking.
- **`artifacts/` vs `findings/`**: `artifacts/` is per-run and holds the
  live record (`state.json`, `dev-diary.md`) that gets built up across
  runs. `findings/` is for durable write-ups that should survive long after
  the task that produced them is forgotten.
- **Two consecutive verification failures stop the loop** rather than
  retrying forever — the coordinator reports and asks, it doesn't grind,
  and it leaves the task branch unmerged so you can inspect it.
