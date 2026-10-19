# Agent permissions

Which commands an AI agent may never run in this project, and which it may run without
asking. Written once, for any agent. Each agent enforces it differently, so this file is
the source and each agent's own configuration is a copy of it.

## Never run (hard block)

These change git history or throw work away. I review and commit myself.

| Command | Why |
|---|---|
| `git add` | staging is my decision |
| `git commit` | I commit myself |
| `git push` | publishing is my decision |
| `git rm` | deletes files from git |
| `git reset` | can throw away work |
| `git checkout` | can overwrite uncommitted work |
| `git restore` | throws away uncommitted changes |
| `git clean -f`, `git clean -x` | permanently deletes untracked or ignored files (`output/`, `scratch/`, `.env`) |

## Allowed without asking (read-only or safe)

| Command | Why |
|---|---|
| `git status`, `git diff`, `git log`, `git show`, `git check-ignore` | read-only |
| `.venv/bin/python -m pytest` (any arguments) | runs the tests; changes nothing |
| `.venv/bin/python -m py_compile <file>` | syntax check |

Everything else follows the normal rule: ask first.

## Making it effective (for the agent reading this)

Writing these rules down is not enough: an instruction can be missed, and a hard block
can't. So, the first time you work in this project:

1. Check whether your tool can enforce command rules itself (a deny list, a policy file,
   an approval setting). Use your tool's **current documentation**, not memory: these
   formats change.
2. If it can and it isn't set up yet, tell me which file you'd create or change, what it
   would contain, and why, then **wait for my authorization**.
3. Once authorized, write it so the blocks and allowances above match exactly, and show
   me how you checked it works (for example, a blocked command being refused).
4. If your tool can't enforce rules, say so, and follow this file as an instruction.

When this file changes, update every agent's configuration the same way. This file wins
if they disagree.
