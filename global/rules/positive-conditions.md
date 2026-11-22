# Write conditions positively

In code I'll read, don't write chains of negative conditions to skip things:
`if not x or y != z: continue`. I find "not", mixed with "or" and "!=", very hard
to follow, because every condition has to be read backwards.

Instead:
- Give each condition a name that says what it means, in the positive
  (`is_change_log`, `has_author`, `value_changed`).
- Join them with `and`, and do the work inside the `if`:
  `if has_author and includes_x and value_changed: ...`
- When a loop needs a filter, move the test into a small helper that answers one
  question ("is this a real change?") and keep the loop to "if yes, record it".
- Comparing with `!=` is fine when it IS the rule ("the value changed"), but put it
  in a named variable so the name carries the meaning, not the symbol.

Scope: new or rewritten code. Don't rewrite existing code into this style unless I
ask; I'll do that on purpose, in its own session.

Why: 2026-11-18, in a work project. I couldn't follow a function's chain of
`if not …: continue` filters. Rewritten with named positive conditions, it read as
plain language.
