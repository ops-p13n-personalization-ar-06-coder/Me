# Aurora Workflow Checklist (every new problem)

## Plan
- Choose **category** (Bug Fix / Completion) and domain.
- Re-read `aurora_canon_v2025-09-19.md` (rules + fairness).

## Author
- Emit only **four artifacts**, in order; ASCII-only; deterministic.
- Description includes:
  - Title line
  - Full API/CLI spec
  - **Exact** error messages and **error precedence**
  - Input/output formats, normalization/ordering rules
  - Edge cases and boundaries
  - ≥2 success and ≥1 error **examples** with exact outputs
  - **Difficulty & Fairness** subsection (why <30%, which levers used, how ambiguity avoided)

## Tests (solution_test.py)
- Deterministic; **no comments/docstrings**.
- Import only from `solution`.
- Assert **exact strings** (+ CLI newline policy).
- Cover: happy paths, **each error** (by precedence), boundaries, normalization/ordering, persistence/duplicates where applicable.
- For Pandas tasks: 2-decimal rounding; **ddof=1**; strict `YYYY-MM-DD` filter inputs; persistence at `datasets/<name>.pkl`.

## Base vs Solution
- **Bug Fix:** base is runnable but buggy; public API unchanged; typical bug surfaces include ordering (merge→transform→validate), deep-merge vs list replace, type coercion, error wording, or boundary checks.
- **Completion:** base has thin stubs (`pass`); CLI via `sys.argv`; deps pinned.
- **Solution:** matches spec; only allowed deps; passes tests.

## Fairness Gate (before merge)
- ≥2 straightforward pass cases present? ✅
- Estimated pass rate <30% without trickery? ✅ If not, add meaningful edge cases or tighten error precedence/ordering rules.
- No claims of “running tests N times.” ✅

## Final hygiene
- Output artifacts named **exactly**: `solution.py`, `solution_test.py`.
- No extra files/prose in the four-artifact output.
- Optional: run `tools/no_comments_check.py` locally to ensure test file has no comments.
