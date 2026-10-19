# how_i_like_my_agents
This is a repo where I store files and folders of how I like my AI agents to work: their rules, approvals, exceptions, etc. It's meant to make transitions into new companies easier for me when setting up my agents.

Everything here is written for **any** coding agent (Claude Code, Codex, or whatever comes
next): plain Markdown as the source, plus small scripts that put it where each agent looks.
Nothing here belongs to an employer: no company names, data, keys or internal processes.

## What's in it

```
global/                       my instructions for every agent, on every project
  rules/                      how to work with me: pacing, one step at a time, stop and
                              ask, ask before editing, no commit reminders, derive don't hardcode
  general_instructions/       how to talk to me and how I set things up: acronyms,
                              yes-man protocol, plan before building, personal repos
  install.py                  installs both folders for each agent on this computer
skeleton/                     the starting point for every new project
new_project.py                creates a new project from skeleton/, ready to work in
```

**The skeleton** is the project structure that has worked for me:

- `my_project/` (renamed per project) for the code, with `paths.py` as the single place
  locations and keys are defined
- `data/` for committed inputs, `output/` for everything a run produces (git-ignored),
  `scratch/` as my sandbox (git-ignored), `docs/` for runbooks, `tests/` with a starter suite
- `.venv` per project, created by `new_project.py`
- `AGENTS.md`: what every agent must know about the project, including "when a change is
  done" (tests, then docs as the last step)
- `CODING_STYLE.md`: how I like code written, with examples (mostly Python)
- `AGENT_PERMISSIONS.md`: commands agents may never run (commits and other git changes)
  and those they may run without asking; each agent turns it into its own hard blocks
- `CLAUDE.md` and `.claude/` for Claude Code specifically (it points to `AGENTS.md`)

## On a new computer (once)

1. Install Python 3.12+ and git. Then clone this repo with my personal GitHub account and
   set it up as described in
   [global/general_instructions/personal-repos.md](global/general_instructions/personal-repos.md).
2. See what the installer would change, without writing anything:
   ```bash
   python3 global/install.py --dry-run
   ```
3. Install. Files that already exist are backed up first (`<name>.backup-<date-time>`):
   ```bash
   python3 global/install.py
   ```
   If a backup had instructions worth keeping, add them to `global/rules/` or
   `global/general_instructions/` and run it again. Then delete the backups.
4. Check it worked: open a **new** session in each agent and ask
   *"Without reading any files, which of my global instructions did you get? Quote the
   first line of Rule B."* It should list all of them.

## Starting a new project

```bash
python3 new_project.py                               # asks for the name and the folder
python3 new_project.py sales_report --dest ~/Code    # or say it directly
```

It copies the skeleton, renames the code folder, creates `output/`, `scratch/` and the
`.venv`, installs, runs the tests and starts git. It commits nothing. Then:

1. Fill in the TODOs in the new project's `AGENTS.md` and `README.md`.
2. The first time an agent works there, it sets up its own command blocks from
   `AGENT_PERMISSIONS.md` (it asks first).
3. If it's a personal repo, set it up as in `personal-repos.md`.

## Changing my instructions

Edit the files in `global/rules/` or `global/general_instructions/`, never the installed
copies in `~/.claude` or `~/.codex` (the installer overwrites those). One instruction per
file; a new file is picked up automatically. Then run `python3 global/install.py` again
and start a new session.

To support another agent, add a function to `install.py` that writes the same files where
that agent looks for global instructions, the way `claude_files()` and `codex_files()` do.
