# Project Coding — Supreme Guidelines (v2025-09-19)

**Status:** Final • **Source of truth** for authoring Aurora-style programming problems.
**Covers:** Bug Fix & Completion categories with policies distilled from the three reference exemplars:
- Configuration Processor (Bug Fix)
- Data Analysis Dashboard CLI (Completion; Pandas)
- Raft Log Validator (Bug Fix)

---

## 1) Output Contract (always the same)
Produce **exactly four artifacts** in this order (ASCII-only, deterministic):
1. **Description** (markdown)
2. **Unit Tests** — file named `solution_test.py`
3. **Base Code** — file named `solution.py` (buggy for Bug-Fix; stubs for Completion)
4. **Correct Solution Code** — contents for `solution.py` that pass the tests

No extra files or commentary in the final output. Tests must import only from `solution`.

---

## 2) Global Policy (applies to every problem)
- **Determinism:** no network, no randomness, no sleeps; time-stamps may exist but are never asserted by tests.
- **Exactness:** error messages, rounding, spacing, punctuation and newline behavior must be testable and exact.
- **Dependencies:** only stdlib unless the Description explicitly allows pinned libs (e.g., `pandas==2.1.4+`, `numpy==1.26.x`, `openpyxl==3.1.x`).
- **Unknowns:** ambiguous behavior must be specified; prefer explicit ladders (e.g., error precedence, merge rules).
- **Paths & names:** file names are **exactly** `solution.py` and `solution_test.py`; public API names must match the Description.

### Fairness & Difficulty
- **Target pass rate:** **under 30%** for unaided solvers.
- Include **≥2 straightforward success cases** to avoid accidental 0% pass.
- If success rates seem high, add **meaningful** edge cases (not trickery): boundary conditions, stricter precedence, duplicate handling, cross-function interactions.
- Do **not** claim “ran tests N times”; encode fairness by spec + tests.

### Testing Hygiene
- `solution_test.py` contains **no comments or docstrings**; asserts **exact strings**; deterministic only.
- CLI vs API: API returns strings **without** trailing newline; CLI prints **append one** trailing newline (when CLI exists).
- For numeric stats: round to **2 decimals**; sample standard deviation uses **ddof=1**.

---

## 3) Category Canons

### A) Bug Fix
- Keep **public API unchanged**; base code is runnable but contains intentional bugs.
- If a pipeline exists, the order is **merge → transform → validate** (post-transform validation).
- Validation should accept `int` where `float` is required (when specified).
- Unknown/unmodeled fields are preserved unless the spec says otherwise.
- Error wording and precedence are **exact** and must match the Description.

### B) Completion
- Base code provides minimal stubs with `pass` for each public method.
- CLI (when required) uses `sys.argv` only; help/usage texts are **not** normative—only explicit OK/ERROR lines are asserted.
- Persistence or cross-invocation behavior must be documented and tested (e.g., pickles, caches).
- Strict error precedence ladders are mandatory and enforced by tests.

---

## 4) Domain Rules from the Reference Problems

### 4.1 Configuration Processor (Bug Fix)
**Pipeline:** `merge → transform (defaults, coercions, transforms) → validate`.

**Merging**
- Later files override earlier ones.
- **Deep-merge** dictionaries; lists are **replaced** (not concatenated).
- Unknown fields are preserved.

**Transforms**
- Defaults applied for fields with `default` when missing.
- Type coercions (case-insensitive where applicable):
  - `"123" → 123`, `"-45" → -45` (int)
  - `"15.5" → 15.5` (float)
  - `"true"|"1"|"yes"|"on" → True`; any other string → `False`
  - Any value → string via `str(value)` when `type: "string"`
- String transforms: `"uppercase"`, `"lowercase"`, `"strip"`; numeric transform: `"abs"`.
- Nested dicts honor `nested_schema` recursively.

**Validation (after transform)**
- Supported types: `"string"`, `"integer"`, `"float"`, `"boolean"`, `"list"`, `"dict"`.
- Enforce: required fields; `min_value`/`max_value` for numbers; `min_length`/`max_length` for strings/lists; `allowed_values`.
- Nested validation via `nested_schema`.
- **Dot-paths** for nested names, e.g., `database.host`.
- **Exact messages:**
  - Missing: `Required field '{path}' is missing`
  - Type: `Field '{path}' must be {expected}, got {actual}`  (types in lowercase: `str`, `int`, `float`, `bool`, `list`, `dict`)
  - Min value: `Field '{path}' value {v} is below minimum {min}`
  - Max value: `Field '{path}' value {v} is above maximum {max}`
  - Min length: `Field '{path}' length {n} is below minimum {min_n}`
  - Max length: `Field '{path}' length {n} is above maximum {max_n}`
  - Allowed: `Field '{path}' value '{v}' not in allowed values {allowed_list}`

**INI parsing**
- Booleans: case-insensitive `true`/`false`.
- Numbers: if token contains `.`, parse as float; else try int; fallback to raw string.

**Process-all errors**
- On validation failure: raise `ConfigurationError("Configuration validation failed: {e1}; {e2}; ...")`.

---

### 4.2 Data Analysis Dashboard CLI (Completion; Pandas)
**Allowed deps:** `pandas==2.1.4+`, `numpy==1.26.x`, `openpyxl==3.1.x`.

**Commands**
- `load <csv_file> <dataset_name>`
- `describe <dataset_name>`
- `compare <dataset1> <dataset2> <column_name>`
- `export <dataset_name> <output_file>`
- `filter <dataset> <column> <operator> <value> <new_dataset>`
- `merge <dataset1> <dataset2> <column> <new_dataset>`

**File validation**
- Must end with `.csv`; readable by `pd.read_csv`; non-empty; must have proper headers (first row not all numeric tokens).
- Any failure → `"ERROR: invalid file format"`.

**Persistence**
- On `load`: save to `datasets/<name>.pkl` and keep in-memory cache.
- Other commands may source from cache or pickle if not cached.

**Type inference priority**
1) All tokens numeric → numeric
2) Common dates → datetime64[ns] (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY, `"Jan 1, 2023"`-style)
3) Otherwise text (`object`)
4) Ambiguous numeric-like (e.g., `"2023"`) → numeric

**Missing values**
- Empty strings are missing.
- Numeric: if a mode exists with frequency ≥2, fill with the **numerically smallest** mode; else use **median**.
- Text: fill with mode; ties resolved by **lexicographically smallest** token.

**Outputs**
- Numeric stats: count, mean, std, min, 25%, 50%, 75%, max (2 decimals; std uses ddof=1).
- Text/date summaries: `count`, `unique`, `top`, `freq` (dtype for dates shown as `datetime64[ns]`).
- Compare: for numeric columns only; otherwise `"ERROR: column not found"`.
- Export: write Excel; return `OK: dataset <name> exported to <path>`.

**Filter**
- Operators: `> < >= <= == != contains not_contains`.
- Numeric: only comparison/equals ops; text: `contains`/`not_contains` (case-insensitive); dates: comparisons with **strict `YYYY-MM-DD`** input.
- Invalid operator for the column type → `"ERROR: invalid operator"`.
- Parse failure for value → `"ERROR: invalid value"`.
- Empty result → `"ERROR: operation failed"`.

**Merge**
- Inner join on `column`; both datasets must have it.
- Column types must be compatible (both numeric or both text); else `"ERROR: operation failed"`.
- Duplicate columns adopt pandas defaults (`_x`, `_y`).

**Error precedence ladder**
1) `"ERROR: file not found"`
2) `"ERROR: invalid file format"`
3) `"ERROR: dataset not found"`
4) `"ERROR: column not found"`
5) `"ERROR: invalid operator"`
6) `"ERROR: invalid value"`
7) `"ERROR: operation failed"`

**CLI vs API newlines**
- API returns strings **without** trailing newline; CLI prints add **one**.

---

### 4.3 Raft Log Validator (Bug Fix)
**Entry format**
```python
{"term": int, "index": int, "data": Any, "timestamp": float}
```
Indices start at **1**.

**append_entry(term, data, prev_log_index=None, prev_log_term=None) → dict**
- Reject on `term < current_term` with `"Term is lower than current term"`.
- If `term > current_term`, set `current_term = term` and `voted_for = None`.
- Previous-log checks:
  - If both provided and out of range (negative or `> len(log)`), fail `"Previous log index out of range"`.
  - Sentinel `(0, 0)` is valid.
  - If provided and exists, require matching term; else `"Previous log entry mismatch"`.
- Compute new index:
  - If `prev_log_index` provided → `new_index = prev_log_index + 1`; else `len(log)+1`.
- Conflict handling:
  - If an entry exists at `new_index` with a **different term**:
    - If `new_index > commit_index`: **truncate** to `new_index-1` then append.
    - Else: fail `"Cannot overwrite committed entries"`.
- Success response: `{"success": True, "current_term": current_term, "log_index": new_index, "message": "Entry appended successfully"}`.

**commit_entries(leader_commit_index) → dict**
- Fail if `leader_commit_index > len(log)`.
- Never decrease commit index; if lower, return success with `committed_count=0`.
- Validate no gaps from 1..leader_commit_index.
- On success: set commit index; return `{"success": True, "committed_count": delta, "commit_index": value}`.

**advance_term(new_term) → bool**
- Advance only if strictly higher; reset `voted_for=None` on advance.

**get_term_for_index(i) → int**
- `0 → 0`; invalid/non-existent → `-1`; otherwise the entry term.

**get_log_info() → dict**
```python
{
  "node_id": str,
  "current_term": int,
  "log_length": int,
  "commit_index": int,
  "last_log_index": int,  # 0 if empty
  "last_log_term": int,   # 0 if empty
  "voted_for": str | None
}
```

**Safety properties**
- Term numbers strictly monotonic.
- Committed entries are never truncated/overwritten.
- If two logs contain an entry with the same (index, term), all preceding entries are identical.

---

## 5) Anti-Patterns (hard no)
- Hidden/implicit behavior that tests depend on.
- Network/file IO beyond what the Description permits.
- Non-deterministic tests or reliance on local environment/locale.
- Error strings that don't match **exact** wording/casing/punctuation.
- Changing public API between base and solution in Bug Fix category.

---

## 6) Versioning
- This document is **v2025-09-19**. Any later edits must bump the date and list changes at the top.
