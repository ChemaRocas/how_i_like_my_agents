# how_i_like_my_agents
This is a repo where I store files and folders of how I like my AI agents to work: their rules, approvals, exceptions, etc. It's meant to make transitions into new companies easier for me when setting up my agents.

Everything here is written for **any** coding agent (Claude Code, Codex, or whatever comes
next): plain Markdown as the source, plus small scripts that put it where each agent looks.
Nothing here belongs to an employer: no company names, data, keys or internal processes.

## What's in it

```
global/                       my instructions for every agent, on every project
  rules/                      how to work with me: pacing, one step at a time, stop and
                              ask, ask before editing, no commit reminders, derive don't
                              hardcode, show me the edits, how to ask me questions, SQL style,
                              write conditions positively
  general_instructions/       who I am and how to talk to me, and how I set things up:
                              about me, acronyms, yes-man protocol, plan before building,
                              personal repos, side sessions are independent
  local_templates/            templates for one computer or one job, filled in and kept
                              outside this repo (not installed): what I'm working on now
  skills/                     procedures agents load when needed: gitignore-audit (runs
                              whenever a .gitignore changes, or when I ask),
                              check-docs-contradictions (only when I ask) and
                              presentation-slide-deck-helper (whenever I ask for a
                              presentation or slide deck)
  install.py                  installs all of the above for each agent on this computer
  HOW_TO_WRITE_A_RULE.md      where a new rule goes, its shape, and how it becomes global
skeleton/                     the starting point for every new project
new_project.py                creates a new project from skeleton/, ready to work in
tests/                        tests for install.py, new_project.py and the permissions
AGENTS.md                     notes for an agent working in this repo (CLAUDE.md points here)
```

**The skeleton** is the project structure that has worked for me:

- `my_project/` (renamed per project) for the code, with `paths.py` as the single place
  locations and keys are defined
- `data/` for committed inputs, `output/` for everything a run produces (git-ignored),
  `scratch/` as my sandbox (git-ignored), `docs/` for runbooks, `tests/` with a starter suite
- `.venv` per project, created by `new_project.py`
- `AGENTS.md`: what every agent must know about the project, including "when a change is
  done" (tests, then docs as the last step)
- `CODING_STYLE.md`: how I like code written, with examples (mostly Python), including when
  to add a dry run, a resume option or a lock
- `skills/`: a place for project-specific skills, with a suggested (not required) shape
- `AGENT_PERMISSIONS.md`: commands agents may never run (commits and other git or GitHub
  changes), those that need my OK every time, and those they may run without asking; each
  agent turns it into its own blocks
- `CLAUDE.md` and `.claude/` for Claude Code specifically (it points to `AGENTS.md`)

## On a new computer (once)

1. **Install the tools:** Python 3.12+, git, and the GitHub command line `gh`
   (Mac: `brew install python git gh`; Windows: `winget install Python.Python.3.12 Git.Git GitHub.cli`).
   Check with `python3 --version`, `git --version`, `gh --version`.
2. **Sign in to GitHub with both accounts,** the work one (if the job has one) and the
   personal one (ChemaRocas). Run this once per account and follow the prompts:
   ```bash
   gh auth login
   gh auth setup-git
   ```
   The first command signs in; the second makes git use those logins.
3. **Leave the work account as the active one**, permanently (`<work-account>` is its
   GitHub username):
   ```bash
   gh auth switch --user <work-account>
   gh auth status
   ```
4. **Clone this repo with the personal account**, without switching:
   ```bash
   GH_TOKEN=$(gh auth token --user ChemaRocas) gh repo clone ChemaRocas/how_i_like_my_agents
   ```
5. **Set up the clone as a personal repo** (private GitHub email for commits, and its own
   setting so it always uses the personal login), as described in
   [global/general_instructions/personal-repos.md](global/general_instructions/personal-repos.md).
   Check it: `git push --dry-run` must succeed with the work account still active.
6. **See what the installer would change,** without writing anything:
   ```bash
   python3 global/install.py --dry-run
   ```
7. **Install.** Files that already exist are backed up first (`<name>.backup-<date-time>`):
   ```bash
   python3 global/install.py
   ```
   If a backup had instructions worth keeping: general ones go into `global/` (then run the
   installer again); ones for this computer or this employer only go in the local places
   described under "Changing my instructions". Then delete the backups.
8. **Check it worked:** open a **new** session in each agent and ask
   *"Without reading any files, which of my global instructions did you get? Quote the
   first line of Rule B."* It should list all of them.

## Starting a new project

```bash
python3 new_project.py                               # asks for the name and the folder
python3 new_project.py sales_report --dest ~/Code    # or say it directly
```

It copies the skeleton, renames the code folder, creates `output/`, `scratch/` and the
`.venv`, installs, runs the tests and starts git. It commits nothing. It refuses names that
would break the project (a skeleton folder like `data`, or the name of a library) and never
creates a project inside this repo. Then:

1. Fill in the TODOs in the new project's `AGENTS.md` and `README.md`.
2. The first time an agent works there, it sets up its own command blocks from
   `AGENT_PERMISSIONS.md` (it asks first).
3. If it's a personal repo, set it up as in `personal-repos.md`.

## Changing my instructions

Edit the files in `global/rules/`, `global/general_instructions/` or `global/skills/`,
never the installed copies (the installer overwrites those). One instruction per file, one
folder per skill; a new one is picked up automatically, and one you delete or rename here
is retired from the agents on the next install (kept as a backup). Then run
`python3 global/install.py` again and start a new session. To write a new rule, follow
[global/HOW_TO_WRITE_A_RULE.md](global/HOW_TO_WRITE_A_RULE.md).

Instructions you want on **one computer only** (for example, ones an employer requires)
never go in this repo. Put them by hand in:

- **Claude Code:** a file in `~/.claude/rules/`. The installer leaves that folder's other
  files alone.
- **Codex:** below the line `<!-- local: kept by install.py -->` at the end of
  `~/.codex/AGENTS.md`. Everything below it survives every install.

At each new job, or when my personal projects change, I can fill in
[global/local_templates/working-on-now.md](global/local_templates/working-on-now.md) and put
it in those places, as its [README](global/local_templates/README.md) explains: it tells
every session what I'm working on (a job, personal projects, or both), alongside the
generic `about-me.md`. It's optional: without it, sessions get only the generic profile.

To support another agent, add a function to `install.py` that writes the same files where
that agent looks for global instructions, the way `claude_files()` and `codex_files()` do.

## Testing this repo

After changing `install.py`, `new_project.py` or the skeleton's permissions, run the tests.
They only ever write to temporary folders, never to your home folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest tests
```

They check that the installer writes, backs up and retires the right files; that
`new_project.py` builds a complete project and refuses names or folders that would break
it; and that `skeleton/.claude/settings.json` matches the tables in
`skeleton/AGENT_PERMISSIONS.md`.
