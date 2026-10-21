# <Process name>

<!-- Copy this file to docs/<process-name>.md and replace every <...>. Delete a section
     only if it truly doesn't apply; write "None" instead when its absence is the news. -->

One or two sentences: what this process does, for whom, and when it runs (by hand, daily,
monthly).

## How to run it

```bash
.venv/bin/python -m my_project.<module>              # the normal run
.venv/bin/python -m my_project.<module> --dry-run    # everything except spending or writing
```

What it needs before it starts (keys in `.env`, an input file, being online), and where its
results go (always under `output/`).

## What it prints

What a normal run looks like, step by step, and what the end summary means. Include an
example of the summary if it has numbers that need reading.

## What stops it, and what only warns

| Situation | What happens | What to do |
|---|---|---|
| <a check that fails before spending or writing> | **Stops**, nothing written | <how to fix it> |
| <something unusual but survivable> | **Warns** and continues; listed in the summary | <whether to act> |

## If something goes wrong

The failures that have actually happened or are likely, each with what you see and what to
do. If the run takes long and can resume, how to continue it (`--resume`) instead of
starting over.

## Why it works this way

The decisions a reader would otherwise question or "fix": why this filter, why this order,
why this limit. Link the code where the reasoning lives in a docstring.

## Settings you may change

| Setting | Where | Default | Effect |
|---|---|---|---|
| <a constant or .env key> | `my_project/<module>.py` | <value> | <what changing it does> |

## Not in scope

What this process deliberately doesn't do, so nobody adds it by accident.

## History

Dated changes that changed how it behaves or how to run it, newest first, with why.
Keep entries even after something is undone.

- **<YYYY-MM-DD>:** <what changed and why>.
