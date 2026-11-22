# local_templates/

Templates for instructions that belong to **one computer or one job**, so they never go in
this repo filled in. `install.py` doesn't install anything from this folder: you copy a
template, fill it in, and put it where your agents look.

## working-on-now.md

What I'm working on right now: a job (role, team, project, goals), personal projects, or
both. **It's optional.** Without it, sessions still get the generic profile; nothing
expects a job. On a computer for personal work, either skip it or fill in only the
personal-projects part. It complements
[global/general_instructions/about-me.md](../general_instructions/about-me.md), which
holds the part of "who I am" that doesn't change between jobs. Together they give every
session, in any folder, a picture of me and my situation.

**How to fill it in:**

1. Copy [working-on-now.md](working-on-now.md) and say what the computer is for (a job,
   personal projects, or both). Delete the job-only or personal-only lines that don't
   apply, then replace every remaining `<...>`. Delete any other line that doesn't apply
   rather than leaving a placeholder.
2. Keep it under a page. It loads on every message, so write what would change how an
   agent helps you, not a CV.
3. Write roles and general descriptions. No keys, passwords, customer data or numbers that
   would hurt if the file were seen: it's a plain text file on your computer.
4. Date it, and update it when the project, role or priorities change. At the end of a job,
   rewrite it (for example, for personal projects only) or delete it.

**Where to put it** (so every session gets it, whatever folder you open):

- **Claude Code:** save it as `~/.claude/rules/working-on-now.md`. Claude Code loads that
  folder on its own, and `install.py` leaves files it didn't install there alone.
- **Codex:** paste its text below the line `<!-- local: kept by install.py -->` at the end
  of `~/.codex/AGENTS.md`. Everything below that line survives every install.
- **Any other agent:** wherever it reads global instructions.

**Never commit the filled-in version to this repo.** It can describe an employer, and this
repo is generic.

**Check it worked:** open a new session and ask *"Without reading any files, what am I
working on right now?"*
