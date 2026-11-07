---
name: check-docs-contradictions
description: Find and verify stale, contradictory or missing documentation in the current repo against its code, and propose fixes; edits nothing until the user approves. Run only when the user asks for it (a docs check, documentation drift, contradictions in the docs).
disable-model-invocation: true
---

# Check the docs for contradictions

Finds where a repo's documentation has drifted from its code, verifies every finding
against the code, and proposes fixes. **It stops after the proposal:** nothing is edited
until the user gives a go.

Why it exists: docs go stale silently. Pages name scripts that were renamed, a number is
written in six places and updated in one, a README describes a login the opposite way from
the code, links point to deleted pages. Nothing fails, so nobody notices until someone
follows a wrong pointer. The first sweep that used this method found ~50 real problems in
one repo.

Run it only when the user asks. It follows the repo's own rules (its `AGENTS.md`); this
skill adds the procedure.

## Step 0: Ask for the scope

Read the project's run log first, if it has one: `docs/doc-checks-log.md`. Then ask, in one
message, whatever the user didn't already say when calling you:

1. **A full sweep, or only what changed since when** (a date or a commit)? Offer the last
   run's commit as the default.
2. **Which model and effort for the finding pass** (see Step 1)?

- **Full sweep:** every document listed under "What to check". Expensive on a big repo;
  worth it every few months or before handing a project over.
- **Since a date or commit:** list what changed (`git diff --name-only <commit>`, or for a
  date `git log --since=<date> --name-only --format=`), plus uncommitted changes
  (`git status --short`). The scope is then:
  - the changed documents;
  - the documents that describe the changed code (search the `.md` files for each changed
    file's name and module path);
  - the documents that link to the changed documents.

Tell the user the resulting file list before starting.

## What to check

- `AGENTS.md`, `README.md`, every README inside the code folders, everything in `docs/`.
- The project's skills and their reference files.
- The docstring at the top of each code module, and the comments directly above
  module-level constants.
- `.env.example`, and the list of real commands (in Python, `[project.scripts]` in
  `pyproject.toml`).

**Not in scope:** comments inside function bodies; anything under `output/`, `scratch/`,
`.claude/worktrees/` or other git-ignored folders; `.env`. Data and generated files can
hold personal or customer data: a stray one found outside `output/` is reported as a side
finding, never opened.

## Step 1: Find (read-only)

A separate agent makes a better reviewer (it reads with fresh eyes), but the biggest model
at the highest effort can be overkill and costly. **Before launching anything, ask the
user** (in the Step 0 message): list the models and effort levels your tool can use for a
separate reviewer, with your recommendation for this scope (a small "since" check rarely
needs the top option) and a rough sense of the cost difference. The user's benchmark for a
full sweep is **Claude Opus 5.0 with extra effort**: say how each option compares to it.
Wait for the choice. If your tool can't launch a separate agent, say so and do the finding
pass yourself.

The finding pass is **strictly read-only**: no edits, no git writes, no pipelines, no calls to
databases or paid APIs. It follows the repo's reading rules: read code and docs whole, not
by keyword search; stop and report instead of reading a very large file; never open data or
generated files.

It produces:

1. Numbered **claims**, each one problem, with:
   - the file and line;
   - the kind: *stale* (the doc describes code that changed), *contradiction* (two docs,
     or a doc and the code, disagree), *broken pointer* (a file, path, command or section
     that doesn't exist), or *missing* (something a newcomer needs that's written nowhere);
   - what the doc says, and what the code (or the other doc) says.
2. **Side findings:** things that aren't doc problems but showed up (a stray data file, an
   old worktree, a note addressed to agents).
3. Every file read in full, and the ones only skimmed.

A separate agent's report is model output, not fact. Step 2 exists because of that.

## Step 2: Verify every claim yourself

Check each claim against the files themselves, not against a summary: read the cited lines
and the code they describe. Give each a verdict:

- **True:** real, as described.
- **Partly true:** real, but overstated or narrower (say how).
- **False:** not a problem (say why).

Report in a table per area (for example: how sessions find the docs; the READMEs and
skills; `docs/`; code comments and side findings): claim, verdict, evidence with file and
line. Over ~30 claims, offer to report one area per turn.

**The code is the source of truth.** When documents disagree with each other, use the
trust order in the repo's `AGENTS.md` if it gives one; otherwise: the code and its
docstrings, then `AGENTS.md`, then skills, then READMEs, then `docs/`.

For side findings that involve personal or customer data, check only that the file exists,
its size, and whether git ignores it. Don't open it.

## Step 3: List the disagreements about what SHOULD happen

Some findings aren't "the doc is out of date" but "a comment and the code disagree about
intent". Example: a comment says a cache lasts 1 hour "because batches are slow", while the
code sets 5 minutes. The code wins for now, but the code might be what's wrong.

List every case like this separately, with both versions and their file and line, and ask
the user which is right. **Don't resolve them yourself.**

## Step 4: Propose the fixes, then stop

Group the fixes into steps the user can approve one at a time, for example:

1. Code comments and docstrings (comments only, never behaviour).
2. READMEs inside the code folders.
3. Skills and their reference files.
4. `docs/`.
5. `README.md` and `AGENTS.md`.
6. Housekeeping: anything that deletes (stray files, old worktrees, pages to merge into
   another). Each deletion needs its own go.

For each step, say which fixes are plain corrections and which need a decision. End with
all open questions numbered, each with your recommendation and what changes depending on
the answer.

**Then record the run and stop.** The one edit a check makes, after saying so in the chat,
is one line in `docs/doc-checks-log.md` (create it the first time, with a one-line title):
the date, the scope (full, or since what), the commit read (`git rev-parse --short HEAD`,
plus "and uncommitted changes" if there were any), and the count of claims by verdict.
Nothing else is edited in this run. The report itself stays in the chat; don't write it to
a file.

## After the user's go (not part of the check)

When the user approves a step, do that step only, following the repo's usual rules:

- Edit with the file editor, not terminal commands, so the user sees every change. If
  something can't go through the editor (deleting a file, creating a link), say so first.
- Change comments and docs only. A fix that would change behaviour is a separate request.
- After renaming or removing something, search the `.md` files for the old name.
- Write file references as links with the full path from the repo root.
- When a document merges into another, move everything it said that the target doesn't
  already say, then delete it, then fix every link to it.
- Run the tests (including any test that checks doc links), and report: files changed,
  what was tested and the result, what wasn't done, and what the next step would do.
- When the last approved step is done, add to that run's log line which steps were fixed
  and which were skipped.
