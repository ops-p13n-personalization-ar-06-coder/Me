
---

### 2) `HINTS_FOR_SOLVERS.md`  (optional, nice to have)

```markdown
# Hints for Solvers (Optional Reading)

These examples are designed to be **precise and deterministic**. A few tips:

- **Read 01-description.md carefully.** The tests encode exactly what it says (types, messages, edge cases).
- **Match messages exactly.** If a failure says `"Term is lower than current term"`, don’t rephrase it.
- **Preserve invariants.** E.g., committed entries must never be truncated; deep-merge semantics; CLI output formats line-by-line.
- **Coercion rules matter.** For config/data problems, the order and rules of type inference and transforms are frequently tested.
- **Don’t depend on unspecified behavior.** If it’s not in 01-description.md, tests won’t require it.

Debugging checklist:
- Re-run a single failing test with `-k`:
  ```bash
  pytest -q 02-tests.py -k "name_of_test"
