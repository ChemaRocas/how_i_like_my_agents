# Coding style

How I like code to be written in my projects. It applies mostly to **Python**; in
other languages, keep the same ideas (explain why, sections, one source of truth) in
that language's usual form.

The goal: someone who opens a file for the first time (me, another agent, a colleague)
understands what it does, how to run it and why it's built that way, before reading a
single function.

## The rules

1. **Every module opens with a docstring in titled sections:**
   - *What it does*: the problem and the approach, including why it's done this way.
   - *Pipeline* (when there are steps): the steps, numbered.
   - *Auth* (when it uses keys): where they come from, and that they're never printed.
   - *Run*: the exact commands to copy and paste, with the main options.
   - Add sections when useful (*Resume*, *Output*), always with the same layout.
2. **Banners split the module into blocks:** `Configuration` first, then one block per
   pipeline step, **numbered to match the docstring**, then `Main`. Smaller sub-banners
   (`# --- Name ---`) group related constants inside a block.
3. **Constants live at the top**, in `Configuration`, each with a comment saying why it
   has that value. No magic numbers inside functions.
4. **Every function starts with a one-line docstring** that says what it returns or does.
5. **Comments explain *why*, never *what*,** and sit right before the line that needs
   them: a decision, a guard, an API quirk, a value that looks wrong but isn't. If a
   comment only repeats the code, delete it.
6. **Long functions are split into steps,** each opened by a short comment saying what
   the step does and, when it isn't obvious, why.
7. **Output:**
   - *Automated pipelines* (run on a schedule or by another script) use `logging`, with
     this format, so every line has a time and a level:
     `logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s  %(message)s", datefmt="%H:%M:%S")`
   - *Tools a person runs by hand* use `print`: progress per item (`[3/7] file.pdf ... done`)
     and a summary at the end with counts and anything that failed or was skipped, and why.
8. **Language:** code and comments in English. Domain terms may stay in the business's
   language (a column called `factura`, a status called `pendiente`): don't translate them.
9. **Never print or log a key**, not even partly. Read keys with `paths.require_env()`.
10. **Locations come from `paths.py`**: never build a path from `__file__` or hardcode one.
11. **Cost and production risk.** Use each of these where it applies, not everywhere:
    - **`--dry-run`** for anything that spends money (paid APIs) or writes to shared
      systems (a shared drive, a database, a production spreadsheet): it does everything
      except the expensive or irreversible part, and says what it would have done.
    - **`--resume`** (optional) only for runs that take long (more than ~5 minutes) and can
      die halfway, for example on a lost connection: it continues from where the run
      stopped instead of starting over or paying twice. Don't add it to short runs.
    - **A lock** (a second copy of the same process is refused, not queued) only for long
      pipelines, where two copies at once would overwrite each other's state.
    - **Refuse instead of guessing:** when an input is ambiguous or a check fails before
      spending or writing, stop with a clear message rather than picking a default.
    - **A test mode that can never write to production:** if the project has a way to try
      things on real inputs, its results go to a separate place, and the production
      writers refuse to run in that mode.

## Example 1: how a module opens

The docstring and the banners. A reader knows what the file does, its steps and how to
run it before reaching any code.

```python
"""
Invoice export: turns a day of invoices from the billing API into a CSV for the
finance team's spreadsheet.

What it does
------------
Downloads the day's invoices, keeps the ones that are final (drafts change and would
make yesterday's totals move), converts amounts to one currency, and writes one CSV row
per invoice. Invoices that can't be converted are not dropped: they're written with an
`error` column filled in, so the spreadsheet shows the gap instead of hiding it.

Pipeline
--------
  1. Download the day's invoices (paginated; the API caps a page at 100).
  2. Keep final invoices only.
  3. Convert every amount to EUR with that day's rates.
  4. Write output/invoices/YYMMDD_invoices.csv and print a summary.

Auth
----
BILLING_API_KEY is read from .env through paths.require_env(). It is never logged.

Run
---
    python -m my_project.invoice_export                 # yesterday
    python -m my_project.invoice_export 2026-10-01      # a specific day
    python -m my_project.invoice_export --dry-run       # everything but the write
"""

import argparse
import csv
import logging
from datetime import date, timedelta

from my_project import paths

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# --- Billing API -------------------------------------------------------------
API_URL = "https://billing.example.com/v2/invoices"
PAGE_SIZE = 100          # the API's maximum; asking for more silently returns 100

# --- Conversion --------------------------------------------------------------
TARGET_CURRENCY = "EUR"  # the currency of the finance team's spreadsheet
ROUNDING = 2             # cents: the spreadsheet compares totals to the cent


# --------------------------------------------------------------------------- #
# 1. Download
# --------------------------------------------------------------------------- #
```

## Example 2: a small function

One-line docstring, and a comment only where a reader would otherwise "fix" something.

```python
def invoice_day(invoice):
    """The day an invoice counts for: its issue date, in the company's timezone."""
    # Not the creation timestamp: invoices are often created the evening before and
    # issued the next morning, and finance counts them on the day they were issued.
    return invoice["issued_at"].astimezone(COMPANY_TZ).date()


def amount_in_target(amount, currency, rates):
    """The amount converted to TARGET_CURRENCY, or None if there's no rate for it."""
    if currency == TARGET_CURRENCY:
        return round(amount, ROUNDING)
    rate = rates.get(currency)
    # None, not 0: a missing rate must show up as an error row, and a 0 would look
    # like a real (free) invoice in the totals.
    if rate is None:
        return None
    return round(amount * rate, ROUNDING)
```

## Example 3: a longer function, split into steps

Each step opens with a comment; the steps match the Pipeline in the module docstring.
This is a pipeline, so it logs; a hand-run tool would `print` instead.

```python
def main():
    """Run the export for one day: download, filter, convert, write."""
    args = parse_args()
    day = args.day or date.today() - timedelta(days=1)
    api_key = paths.require_env("BILLING_API_KEY")

    # 1. Download. Every page is fetched before anything is written, so a failure
    #    halfway through leaves no half-written CSV behind.
    invoices = download_invoices(day, api_key)
    log.info("downloaded %d invoices for %s", len(invoices), day)

    # 2. Final invoices only: drafts can still change, which would move totals
    #    that finance has already reported.
    final = [inv for inv in invoices if inv["status"] == "final"]
    log.info("kept %d final invoices (%d drafts skipped)", len(final), len(invoices) - len(final))

    # 3. Convert. Rates are fetched once for the day, not per invoice: the same day
    #    must always produce the same totals, whenever the export is re-run.
    rates = download_rates(day)
    rows = [to_row(inv, rates) for inv in final]
    errors = [row for row in rows if row["error"]]

    # 4. Write, unless this is a dry run. Error rows are written too (see the module
    #    docstring): a missing invoice must be visible in the spreadsheet.
    if args.dry_run:
        log.info("dry run: would write %d rows (%d with errors)", len(rows), len(errors))
        return
    out = paths.output_dir("invoices") / f"{day:%y%m%d}_invoices.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:  # -sig: spreadsheets read accents
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["error"])
        writer.writeheader()
        writer.writerows(rows)
    log.info("wrote %s: %d rows, %d with errors", out.name, len(rows), len(errors))
    if errors:
        log.warning("%d invoices could not be converted; see the error column", len(errors))
```
