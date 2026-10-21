# Agent permissions

Which commands an AI agent may never run in this project, which need my OK every time,
and which it may run without asking. Written once, for any agent. Each agent enforces it
differently, so this file is the source and each agent's own configuration is a copy of it.

## Never run (hard block)

These change git history or the working tree, throw work away, or publish something.
I review, commit and publish myself. They're blocked **however they're written**: with
extra flags, in another order, or through `git -C <folder> ...`.

| Command | Why |
|---|---|
| `git add` | staging is my decision |
| `git commit`, `git revert`, `git cherry-pick` | they create commits; I commit myself |
| `git push`, `git tag` | publishing is my decision |
| `git rm`, `git mv` | change what git tracks |
| `git reset`, `git restore` | throw away work |
| `git checkout`, `git switch` | can overwrite uncommitted work |
| `git clean` (any flags, even `-n`) | permanently deletes untracked or ignored files (`output/`, `scratch/`, `.env`) |
| `git stash` | hides or drops uncommitted work |
| `git rebase`, `git merge` | rewrite or combine history |
| `git branch -d`, `git branch -D`, `git branch --delete` | delete branches |
| `gh pr create`, `gh pr merge`, `gh repo create`, `gh repo delete`, `gh release create` | publish or delete on GitHub |

## Ask first, every time

| Command | Why |
|---|---|
| `git config` | changes settings that persist (identity, credentials); see my personal-repos instructions |

## Allowed without asking (read-only or safe)

| Command | Why |
|---|---|
| `git status`, `git diff`, `git log`, `git show`, `git check-ignore` | read-only |
| `.venv/bin/python -m pytest` (any arguments) | runs the tests; changes nothing |
| `.venv/bin/python -m py_compile <file>` | syntax check |

Everything else follows the normal rule: ask first.

## Limits: what the blocks can and can't do

Tool-enforced command rules usually match the command **as written**. Some variants can
slip past them: `git -C <folder> push`, an alias, a command inside a script or chained
after `&&`. So the blocks are a safety net, not a guarantee. The rule above is what
counts: if a command does what a blocked one does, don't run it, however it's spelled.

## Making it effective (for the agent reading this)

Writing these rules down is not enough on its own; a tool-enforced block is a second line
of defence. So, the first time you work in this project:

1. Look at **Enforcement status** below. If your tool is listed as configured, check the
   configuration still matches this file and skip to step 4.
2. If not, check whether your tool can enforce command rules (a deny list, a policy file,
   an approval setting). Use your tool's **current documentation**, not memory: these
   formats change.
3. If it can, tell me which file you'd create or change, what it would contain, and why,
   then **wait for my authorization**. Once authorized, write it so it matches the three
   tables above (never run / ask first / allowed), show me how you checked it (for
   example, a blocked command being refused), and add your tool to Enforcement status.
4. If your tool can't enforce rules, say so, add it to Enforcement status as "instructions
   only", and follow this file as an instruction.

When this file changes, update every configured tool the same way. This file wins if
they disagree.

## Enforcement status

- **Claude Code:** configured in `.claude/settings.json` (deny, ask and allow lists),
  shipped with the project skeleton.
