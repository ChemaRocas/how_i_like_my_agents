# AGENTS.md

Notes for any AI coding agent working in this repo. Humans: [README.md](README.md).

## What this is

My personal template for working with AI coding agents, meant to move with me from job to
job. It holds:

- `global/`: my instructions for every agent, on every project (`rules/`,
  `general_instructions/`, `skills/`), and `install.py`, which installs them for each agent.
- `skeleton/` + `new_project.py`: the starting point for every new project.
- `tests/`: tests for the scripts above.

## Rules for working in this repo

- **Generic only.** Nothing from an employer goes here: no company names, internal systems,
  data, numbers that identify a business, or keys. If something useful came from a job,
  write the general lesson, not the details.
- **Model-agnostic.** Write instructions for any agent. Tool-specific files (`CLAUDE.md`,
  `.claude/`) only point to or enforce the generic ones; they never hold content of
  their own.
- **Never run `global/install.py` against the real home folder** unless I explicitly ask for
  it in that conversation. To try it, use a test folder:
  `python3 global/install.py --home <a temporary folder>` (add `--dry-run` to write
  nothing at all).
- **Never create a project inside this repo.** Try `new_project.py` with `--dest` pointing
  to a temporary folder (it refuses folders inside the repo anyway).
- **Placeholders:** the skeleton's code folder is `my_project` (also `my-project` and
  `My Project`); `new_project.py` replaces all three. Keep using them in skeleton files.
- My working rules in `global/rules/` apply here too. If you can't find them loaded in
  your session, read them from that folder.
- **New rules** follow [global/HOW_TO_WRITE_A_RULE.md](global/HOW_TO_WRITE_A_RULE.md):
  where each kind goes, the shape (rule, Why with date and incident, How to apply), and
  how a rule is tried in one project before it becomes global.

## If your tool isn't supported by install.py

`install.py` installs for Claude Code and Codex. Any other agent: read every file in
`global/rules/` and `global/general_instructions/` directly and follow them; use the skills
in `global/skills/` when their description says to. To add proper support, write a
function in `install.py` that puts the same files where that agent looks for global
instructions, following `claude_files()` and `codex_files()`, and add tests for it.

## Testing

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest tests
```

The tests only write to temporary folders. When you change `install.py`, `new_project.py`,
or the skeleton's permissions, add or update a test.

## When a change is done

List in your plan the tests and docs you expect to update; my go covers them. Before
reporting a change:

1. **Tests** pass.
2. **Docs, as the last step:** `README.md` (what's in the repo, how to use it), this file,
   and the docstring at the top of any script you changed.
3. **Report** which docs you updated, or why none needed it.

## Git

Stage nothing, commit nothing, push nothing: I review and commit myself.
