# Contributing

## Commit messages

This repo follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>
```

- **type** — one of:
  - `feat` — a new feature or capability
  - `fix` — a bug fix
  - `docs` — documentation only (README, CLAUDE.md, this file, etc.)
  - `refactor` — code change that neither fixes a bug nor adds a feature
  - `chore` — tooling, config, scaffolding, dependency bumps — no source behavior change
  - `test` — adding or correcting tests only
  - `perf` — a change that improves performance
- **scope** *(optional)* — the area touched, e.g. `planner`, `coder`,
  `code-task`, `ci`. Omit it if the change is repo-wide.
- **subject** — imperative mood, no trailing period, under ~72 chars:
  `fix: handle empty TASK.md` not `fixed bug where TASK.md was empty.`
- **body** *(optional)* — the *why*, wrapped at ~72 chars. Skip it for
  changes small enough that the subject says everything.

Breaking changes: add `!` after the type/scope (`feat(coder)!: ...`) and
explain the break in the body.

### Examples
```
feat(planner): investigate codebase directly instead of reading analysis.md

fix(code-task): don't count a rate-limit pause toward consecutive_failures

docs: document the fixed planner/coder model policy in README

chore: ignore .claude/worktrees/ in .gitignore
```

### What NOT to do
- Don't bundle unrelated changes in one commit — one logical change per
  commit, so `git log` stays useful as a record of what happened and why.
- Don't write vague subjects like `update stuff` or `fix things`.
- Don't use `--no-verify` or `--amend` on a commit that's already pushed.

## Workflow

- Commands and conventions for this project live in `CLAUDE.md` — read it
  before making changes.
- The coding workflow is `/code-task`: write a task in `artifacts/TASK.md`,
  run the command, and it drives `planner` (Opus) → `coder` (Sonnet) →
  verification. See `README.md` for the full setup.
- Only the coordinator (`/code-task`, run in the main session) writes
  `artifacts/state.json`. Don't hand-edit it while a run is in progress.
