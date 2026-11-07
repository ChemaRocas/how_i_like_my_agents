# AGENTS.md

Notes for coding agents working in this repo (Claude Code, Codex, or any other).
Humans: [README.md](README.md) is the entry point; runbooks live in [docs/](docs/).

Sections marked TODO are filled in as the project takes shape. Keep the rest: it's the
structure every one of my projects follows.

## Read this first

This file loads automatically; nothing else in the repo does. Before proposing, running or
querying anything, read what the task needs: a session that skips the docs ends up
guessing at things that are written down.

**Every session, whatever the task:** [README.md](README.md) (what the project is, the
commands) and [my_project/paths.py](my_project/paths.py) (where every file lives).

**Then, for the task at hand:**

| Task | Read first |
|---|---|
| TODO: one row per kind of task (a pipeline, a data question, a report) | TODO: the files to read, as links with their full path |
| Anything that costs money or writes to shared systems | *Cost and production risk* below |

**How to read:**

- **Code and documentation** (the `.py`, `.md`, `.sql` files that are part of the repo):
  read them **whole**, not by searching for a keyword; a search only finds what you
  already knew to look for. If a file is over 150 KB, tell me first and read it whole only
  if I say so.
- **Data and generated files** (anything under `output/`, exports, downloaded files): search
  them or read a few lines. Over 50 KB, read one whole only if I say so. They can contain
  personal or customer data: open them only when the task needs them.
- **When two documents disagree, trust in this order:** the code (and its module
  docstrings), then this file, then the project's skills, then other READMEs, then
  `docs/`. Tell me which document you overrode and why.
- Don't search `.claude/worktrees/` or similar folders: they are other sessions' copies of
  the repo, possibly stale.

**Keeping the docs true:**

- **Link every reference by its full path from the repo root.** When a doc names another
  file, write it as a link (`[my_project/paths.py](my_project/paths.py)`), never "the
  README". Every doc should be reachable by following links from this file.
  `tests/test_doc_links.py` fails on a link to a file that doesn't exist.
- **Check the doc against the code you read.** When a task has you read a doc and the code
  it describes, check they agree. If they don't, tell me in your report; the code wins
  meanwhile. Don't go hunting through docs you had no reason to read.
- **After renaming or removing something** (a file, module, command, step or constant),
  search the `.md` files for the old name and fix what you find, or report it.
- **Date decisions, and label history as history.** Write "decided 2026-11-05" or "until
  2026-09-10 …", not a bare "always". A document kept only for the record says so in its
  first line.
- **Every command is listed.** Each command in `pyproject.toml` (`[project.scripts]`)
  appears in the Commands section below; `tests/test_doc_links.py` checks it.
- For a full check of the docs against the code, I can ask for my global
  `check-docs-contradictions` skill.

## What this is

TODO: one paragraph. What the project does, for whom, where its inputs come from and
where its results go.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env      # then fill in the keys
```

Always run Python through `.venv/bin/python`, never the system `python3`: the project's
libraries are installed in `.venv` only, and that's what keeps projects from breaking
each other.

## Commands

```bash
.venv/bin/python -m pytest                                          # the whole test suite
.venv/bin/python -m pytest --cov=my_project --cov-report=term-missing   # with coverage
.venv/bin/python -m my_project.<module>                             # run one module
```

TODO: add each entry point here as it's created, one line each, with what it does.

## The folders that matter

This is the one convention to internalise, because getting it wrong leaks data:

- **`data/`**: inputs the code is built from (templates, reference tables, rubrics).
  Committed.
- **`output/`**: anything a run produces or downloads from an API. **Git-ignored
  wholesale.** It can contain personal or customer data.
- **`scratch/`**: my sandbox for experiments, one-off files and backups. Git-ignored.
  Read it when useful; don't build on it, and don't put anything the code needs there.

Rules that keep data from leaking:

- Run output goes to `output/` (through `paths.output_dir()`), never anywhere else, and
  never into git.
- Never `git add -f` anything from `output/`, `scratch/` or `.env`.
- Keys live in `.env` only. Never in code, never in a committed file, never printed.
- Never commit real data into `data/` or `tests/`. Test data is made up.

## Paths

`my_project/paths.py` is the single source of truth for every location. Import it;
never rebuild the project root (counting `..` levels) and never hardcode an absolute path.

```python
from my_project import paths

source = paths.DATA_DIR / "rubric.xlsx"
results = paths.output_dir("results") / "today.csv"
api_key = paths.require_env("EXAMPLE_API_KEY")   # exits with a clear message if unset
```

A new location goes in `paths.py`, under `DATA_DIR` or `OUTPUT_DIR`. Machine-specific
locations (a synced Drive folder, another disk) go in `.env`, not in code.

## Layout

```
my_project/          the code: one module per step, each runnable on its own
  paths.py           every location, resolved once
data/                committed inputs
docs/                runbooks: how to run and maintain each process
tests/               pytest suite
skills/              project-specific skills for agents (optional)
output/              run results (git-ignored)
scratch/             sandbox (git-ignored)
.claude/             Claude Code settings: git restrictions + helper agents
AGENTS.md            this file (CLAUDE.md just points here)
AGENT_PERMISSIONS.md commands agents may never run / may run without asking
CODING_STYLE.md      how code is written here, with examples
pyproject.toml       dependencies, Python version, test settings
.env.example         names of the keys the project needs
```

TODO: list each module with a one-line description as it's added.

## Conventions

**How the code is written** (module docstrings with sections, banners, one-line
function docstrings, why-comments, logging vs print, language) is in
[CODING_STYLE.md](CODING_STYLE.md), with examples. Read it before writing code here.

**Skills.** Project-specific skills live in [skills/](skills/) (see its README). My global
`gitignore-audit` skill must run whenever `.gitignore` is created or changed, before
reporting the work as done; if it isn't available in your tool, follow its steps from my
global setup.

**Module docstrings explain *why*, not *what*.** Record what you learn the hard way: an
API quirk, why a filter is written a certain way, why a value is a constant. Read the
docstring before changing a module, preserve that reasoning, and add to it.

**Fail loudly, or degrade visibly; never silently.** A record that can't be processed is
logged, skipped and reported in a summary, not dropped. An ambiguous value becomes
`None`/unknown, not a guess. If you're writing `except: pass` or defaulting an ambiguous
value, stop: that breaks the project's core invariant.

**One source of truth.** Anything derived from a source (a spreadsheet, an API, a
config) is derived at runtime, never copied by hand into code or tests.

**Generated files are never hand-edited.** Change the source or the template and
regenerate.

**Each step is an independently runnable module** (`python -m my_project.<step>`). An
orchestrator that runs several steps calls them as separate processes, so one failing
step can't take the others down.

TODO: add project-specific conventions (language of the domain terms, encodings, naming).

## Tests

`pytest`, with no fixture or mocking libraries: pytest's own `tmp_path` and `monkeypatch`,
plus your own fixtures in `tests/conftest.py`, are all you need. The suite must stay fast
(seconds) and must never touch the network.

**Test where bugs are silent:** parsing, rendering, filtering, validation, retries and
pagination. That's where a bug corrupts data without anyone noticing. A crash is loud;
a wrong number in a report isn't.

**Don't test:** `main()` functions that only orchestrate and print, or live API calls
(they cost money and need keys). Fake the API instead: a small hand-written fake object
that returns scripted responses. No mocking library and no recorded responses.

**Every time you touch a parser, validator or renderer, add a case.** Name tests for the
behaviour, not the function (`test_a_missing_id_is_rejected`, not `test_validate_2`), and
put the reasoning in the docstring when the assertion encodes a real decision.

**Derive expected values; don't hardcode them.** Prefer invariants that hold for any input
(weights sum to 100, IDs are unique) over literal counts copied from today's data.

`tests/test_repo_layout.py` guards the structure itself (folders, ignored paths, no
hardcoded paths). Keep it passing.

## Cost and production risk

TODO: list what can cost money or damage shared data in this project, one entry per
hazard: what it is, the date it was found, what happened (with the numbers), and what now
protects against it. Keep the history even after a protection is removed, so nobody adds
it back without knowing why it went. The patterns to protect with (dry run, resume, locks,
refusing instead of guessing, a test mode) are in CODING_STYLE.md, rule 11.

**Agents run only the dry run.** To check that something which spends money or writes
production results works, run its `--dry-run` (or equivalent). Run the real thing only
when I ask for it in that conversation.

## When a change is done

When you propose a change, list in your plan the tests and docs you expect to update. My
go covers them. If you discover another doc or test that needs changing, say so and wait
for a go before touching it.

A change isn't finished when the code works. Before reporting it, in this order:

1. **Tests:** run `.venv/bin/python -m pytest`; all pass. If you touched a parser,
   validator or renderer, a new case covers the change.
2. **Docs, as the last step:** update every document that describes what you changed,
   so nobody (me, another agent, future you) acts on outdated instructions:
   - the runbook in `docs/` for each process you changed (a new process gets a new
     runbook, copied from `docs/RUNBOOK_TEMPLATE.md`): what changed for the person running
     it, and why, with a dated line in its History;
   - `README.md` and the Commands section above, if a command, option or setup step
     changed;
   - the Layout and Conventions sections above, if the structure or a rule changed;
   - the module docstring, if the reasoning behind the code changed;
   - the setup instructions, if the change adds or alters a key, a manual step or a
     machine-specific setting: someone else must be able to set it up on their own
     computer by following them, unaided. Flag anything that only works on my machine.
3. **Report:** say which docs you updated, or why none needed it.

Examples of docs updates that were done well:

- **A new option to continue a run that died.** The runbook's "if it fails" section had
  told the user to reattach by hand with a long command. It was rewritten around the new
  option: the one command to run, which steps it skips, the new message it can print when
  only part of the work was sent, and what to do about it.
- **A safeguard removed after the data proved it unnecessary.** The runbook's warning
  ("never run these two jobs at the same time") was replaced with the new rule, and kept
  the history: the date it was added, what was believed then, and the data that disproved
  it. Without that history, someone would add the safeguard back.
- **A limit added to an export** (only the N most recent files, because the destination
  couldn't take the whole history). The runbook explained the limit and why, how "most
  recent" is decided (by the date in the filename, not the file's modified time, which
  bulk copies rewrite), and that the run's summary lists the files left out, so a missing
  day is never a silent omission.

## Git

Stage nothing, commit nothing: I review and commit myself. The full list of commands
agents may never run, and those they may run without asking, is in
[AGENT_PERMISSIONS.md](AGENT_PERMISSIONS.md). Its last section asks you to enforce it with
your own tool's command rules: do that the first time you work here.
