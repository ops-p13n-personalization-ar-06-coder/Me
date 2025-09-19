# <REPLACE WITH TITLE>

## Description
<Concise, specific objective.>
- Deterministic, ASCII-only; no network/random/time assertions.
- Public API/CLI contract and behaviors (inputs/outputs, formatting, rounding).
- Pipelines and ordering (e.g., merge → transform → validate).
- Unknown-field policy.
- **Exact error messages** and **error precedence ladder**.
- Boundary and edge cases.

### Type/Domain Canon (if applicable)
- Config: types, defaults, coercions, transforms, nested schema, dot-paths, message formats.
- Data: type inference priority, missing-value policy, dates, rounding, persistence, CLI vs API newline rules.
- Raft: append/commit rules, conflict truncation, sentinels, info structure.

### Examples (must be exact)
- ≥2 success examples with exact outputs.
- ≥1 error example per precedence ladder with exact outputs.

### Difficulty & Fairness
- Why target <30% pass.
- Which levers you used (precedence, boundaries, normalization, persistence/dup-collisions).
- How ambiguity is eliminated.

---

## Unit Tests — `solution_test.py`
```python
# <WRITE TESTS HERE — deterministic; no comments/docstrings; assert exact strings; use only public API/CLI; import only from solution>
```

---

## Base Code — `solution.py`
```python
# <Bug-Fix: runnable yet buggy base keeping public API>
# <Completion: minimal stubs with pass for public methods>
```

---

## Correct Solution Code — `solution.py`
```python
# <Fully correct solution matching spec; only allowed deps; passes tests>
```
