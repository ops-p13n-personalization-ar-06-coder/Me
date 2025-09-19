# Project Coding — Workflow Playbook (v2025-09-19)

A practical, step-by-step playbook to create Aurora-style problems that conform to the Supreme Guidelines.

---

## Phase 0 — Bootstrap
- Start from the latest canon (see `Project Coding — Supreme Guidelines (v2025-09-19)`).
- Optional: pull the starter kit (README, canon, checklist, authoring template, tools).

## Phase 1 — Plan
- Pick **category**: Bug Fix or Completion.
- Choose **domain** (e.g., config processing, data analysis CLI, consensus algorithm).
- Draft the **contract**: public API/CLI, inputs/outputs, error messages, precedence ladder, rounding, persistence, boundaries.
- Define **difficulty levers** to target <30% pass (≥2 success cases, meaningful edge/error boundaries).

## Phase 2 — Author the Description
- Use the authoring template sections: Title, Description, Category canon, Examples, Difficulty & Fairness.
- Specify **exact** error messages and the **error precedence** ladder.
- Detail pipelines and ordering (e.g., merge → transform → validate).
- Include ≥2 success and representative error examples with **precise output strings**.

## Phase 3 — Write Tests (`solution_test.py`)
- Deterministic; **no comments/docstrings**; import only from `solution`.
- Assert **exact** strings, including punctuation and newline policy.
- Cover:
  - Happy paths and each error (in precedence order).
  - Boundaries (min/max, empty/non-existent, index 0 special cases).
  - Cross-function interactions (e.g., persistence, truncation safety, duplicate handling).
  - Rounding rules (2 decimals; `ddof=1` for std where applicable).
  - CLI vs API newline contract if a CLI exists.
- Run: `python tools/no_comments_check.py solution_test.py` (expect `OK`).

## Phase 4 — Create Base Code (`solution.py`)
- **Bug Fix:** keep public API unchanged; introduce realistic defects (ordering, deep vs shallow merge, coercion edge cases, off-by-one, precedence).
- **Completion:** provide thin stubs with `pass` for the public surface; no hidden helpers required.
- Ensure base code is runnable and aligned with the Description.

## Phase 5 — Implement Correct Solution (`solution.py`)
- Implement to the letter of the Description and Supreme Guidelines.
- Only allowed dependencies; deterministic behavior.
- Validate edge cases and precedence strictly.

## Phase 6 — Verify Locally
- Execute tests; confirm all pass.
- Manually sanity-check error message casing/punctuation and newline policy.
- For data problems, spot-check rounding (2 decimals) and `ddof=1`.

## Phase 7 — QA Checklist (Green Gate)
- Four artifacts present and in required order.
- Tests: deterministic, no comments/docstrings, exact string assertions.
- Error precedence matches spec (by intentionally triggering each stage).
- Pipelines honored (e.g., config: merge → transform → validate).
- Persistence behavior verified (e.g., `datasets/<name>.pkl` for Data Analyzer).
- Duplicates & collisions behave per canon (e.g., pandas `_x/_y` columns).
- Safety properties (e.g., Raft committed entries never truncated) are enforced by tests.
- Unknown fields policy is explicit and observed.
- Difficulty target plausible (<30%) with at least two unequivocal passing examples.

## Phase 8 — Release & Version
- Place only the four artifacts into the final deliverable.
- Stamp the Description with the date and version (e.g., 2025-09-19).
- If the canon changes, bump versions and update affected problems accordingly.

---

## Category Quick-Checks

### Bug Fix
- Public API unchanged? ✅
- Order of operations correct? (e.g., merge → transform → validate) ✅
- Exact error messages reproduced? ✅
- Boundary cases: nested paths, list replacement vs deep merge, index special-cases. ✅

### Completion
- CLI via `sys.argv` only; OK/ERROR strings match exactly. ✅
- Persistence and cross-run behavior explicit and tested. ✅
- Error precedence enforced; rounding & newline policy correct. ✅

---

## Anti-Regression Notes
- Never introduce nondeterminism or rely on local environment differences.
- Avoid ambiguous/underspecified requirements—tests must reflect the Description precisely.
- Do not broaden dependencies beyond those stated in the Description.

---

**Version:** v2025-09-19. Update this playbook in lock-step with the Supreme Guidelines.
