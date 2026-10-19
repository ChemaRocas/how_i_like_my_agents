# Derive, don't hardcode

Expected values: in validation, self-checks and tests, never hardcode values (counts,
weights, lists of IDs) that can be derived from the source of truth. A hand-written copy
goes stale the moment the source changes; then the check fails on a legitimate edit or
passes while lying. Derive from the parsed source; for drift, compare against the previous
generated output. In tests, prefer invariants that hold for any input (weights sum to 100,
IDs unique) over literal counts.

Identifiers: when a value names an artifact (a file, a table, a sheet), carry it from where
the artifact was actually opened. Don't rebuild it from a pattern (stem + "_suffix"): a
looked-up name states what was read; a built one states what was assumed. Pin it with a
test whose fixture uses a name that does NOT follow the usual pattern.

Why: 2026-09-23, two rejections in a work project: a hand-written table of expected values,
and a filename rebuilt from a suffix instead of the file actually read.
