# Pacing and explanations

On 2026-09-19 I said "You are going way too fast for me" after a turn that chained many
tool calls and produced dense technical output (schemas, permission probes, pre-flight
validation) without first explaining in plain terms what was happening or why.

**Why:** I'm an MBA, not a data engineer. I'm directing the work and need to understand
and approve each step. Volume of correct output is worth less to me than knowing where
things stand and what the next decision is.

**How to apply:**
- Lead with a short plain-language summary of where we are and what the blocker or
  decision is.
- Keep tool calls per turn small: prefer one step, then check in.
- Save schemas, commands and deep detail for after I've asked for them, or put them
  behind a clear heading I can skip.

Related: "Ask before editing" (an explicit go before any file edit) and "Rule B: one
step at a time" (working through a plan).
