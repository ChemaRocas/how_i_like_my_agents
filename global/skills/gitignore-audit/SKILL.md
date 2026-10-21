---
name: gitignore-audit
description: Read-only audit of a git repo's .gitignore against personal/customer data, secrets and build output. Use whenever a .gitignore file is created or changed, or when the user asks to run the gitignore audit. Never edits any file; reports findings and a proposed .gitignore for the user to review.
---

# Gitignore audit

Check whether sensitive files in a git repository are protected by `.gitignore`, and
whether any are already tracked. You only report: you never edit, create or delete a file,
`.gitignore` included. Fixes are proposed for the user to review and apply.

**Run it** whenever a `.gitignore` is created or changed (after the change, before
reporting the work as done), and whenever the user asks for it.

## Boundaries

- Read file contents only to see their structure: the header row of a CSV, the top-level
  keys of a JSON file, the first ~20 lines of a text file. Never print full records or
  secret values.
- Run read-only git commands only: `git ls-files`, `git status --ignored --porcelain
  --untracked-files=all`, `git check-ignore -v`, `git rev-parse`, `git remote -v`. Never
  `git clean` (not even `-n`), and nothing that changes the repo or the working folder.
- If you see a secret value (an API key, a password), don't repeat it: name the file and
  line only ("config.json line 4 looks like an API key").

## What to check for

**A. Personal or customer data**
- Data exports: `*.csv`, `*.xlsx`, `*.json`, `*.parquet` in export- or report-like folders
- Database dumps: `*.sql`, `*.db`, `*.sqlite`, `*.dump`
- Notebooks with saved outputs: `.ipynb` files whose `outputs` fields are filled in
- Screenshots or reports that could show customer data: `*.pdf`, `*.png` in folders such
  as `exports/`, `reports/`, `data/`

**B. Secrets and credentials**
- `.env`, `.env.*` (except `.env.example`), `credentials.json`, `service-account*.json`
- `*.pem`, `*.key`, `*.crt`, `*.pfx`, `id_rsa`, `id_ed25519`
- `.aws/`, `.gcloud/`, `.kube/config`, `*.tfstate`, `*.tfstate.backup`
- `docker-compose.override.yml`, `config.local.*`, `settings.local.*`
- Shell and Python history files: `.bash_history`, `.zsh_history`, `.python_history`

**C. Build output and caches**
- `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, `.venv/`
- `node_modules/`, `dist/`, `build/`, `.next/`
- Model files: `*.pkl`, `*.h5`, `*.pt`, `checkpoints/`
- Logs and temp files: `*.log`, `logs/`, `.cache/`, `*.tmp`

**D. OS and editor noise**
- `.DS_Store`, `Thumbs.db`, `.vscode/`, `.idea/`

**Structured files no pattern covers:** look at the header row or top-level keys only. Flag
the file as "possible personal data" if they include terms like email, phone, name,
address, birth date, national ID numbers, customer id, card, or their equivalents in the
business's language.

## The two checks (always both)

1. **Already exposed (tracked files):** run `git ls-files` and compare every path with the
   categories above. A match is already in git history; `.gitignore` can't undo that.
   Severity: HIGH.
2. **About to leak (untracked files):** run `git status --ignored --porcelain
   --untracked-files=all`. Separate untracked files that `.gitignore` already covers (fine)
   from sensitive ones it doesn't cover: those go into the repo on the next `git add .`.
   Severity: MEDIUM-HIGH.

Say explicitly: "This covers tracked files and untracked files on disk now. It does not
scan git history for secrets committed and later deleted; that needs a dedicated tool such
as gitleaks or trufflehog."

## Report (always these five sections, in this order)

1. **Already covered:** the sensitive categories and patterns the current `.gitignore`
   handles.
2. **Missing patterns:** what isn't covered, with the exact lines you'd add.
3. **Already exposed (HIGH):** tracked files that match a sensitive category. Note that
   ignoring them now does nothing: they need `git rm --cached` (run by the user) and
   possibly a history rewrite.
4. **About to leak (MEDIUM-HIGH):** untracked sensitive files not yet ignored.
5. **Proposed .gitignore:** a full draft, marked "PROPOSAL ONLY: no file has been
   modified", with the existing entries plus your additions, grouped by category with
   comments.

Never skip a section: write "None found" so it's clear the check ran.
