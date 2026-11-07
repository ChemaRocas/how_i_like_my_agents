# SQL style

In every SQL query you write or show me, in any project:

- **Always write `AS`** wherever SQL allows it: column aliases, table aliases, subqueries,
  CTE references, and especially `UNNEST(...) AS name`. Never a bare trailing alias like
  `UNNEST(...) u`.
- **Readable alias names** that say what they hold (`assigned_agent_id`, `orders`), not
  single letters (`u`, `t1`).

**BigQuery only:** a `/* ... */` comment block placed first in a view's body (right after
`AS`) is silently removed when the view is stored. Put the comment after the first keyword
line (`WITH x AS (` or `SELECT`) instead, and read the stored view back to confirm it
survived.

**Why:** 2026-11-06, I couldn't tell what the bare `u` after `UNNEST(...)` meant in a query
an agent showed me; it read as noise. I'm an MBA, not a data engineer: queries I review
must read like sentences. The BigQuery note: header documentation once disappeared from
stored views without any error.
