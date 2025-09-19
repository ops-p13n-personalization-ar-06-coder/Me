# Project Aurora Canon — 2025-09-19 (Source of Truth)

This canon supersedes any older docs. It encodes the final policies from our three gold problems.

---

## Global Rules (apply to every problem)
- Emit **exactly four artifacts** in this order: Description → `solution_test.py` → base `solution.py` → correct `solution.py`.
- **ASCII-only**, deterministic; no network; no random; no sleeps/time-based assertions (timestamps may exist but are never asserted).
- Tests: deterministic; **no comments or docstrings**; assert **exact strings** (and CLI newline behavior); import **only** from `solution`.
- Filenames: **exactly** `solution.py` and `solution_test.py`.

### Fairness & Difficulty
- Target pass rate **<30%** for unaided solvers.
- Include **≥2 clear success cases** to avoid accidental 0%.
- To tighten difficulty (use ≥3 levers when needed): stricter error-precedence; more boundary cases; explicit normalization/ordering; duplicates/collision rules; persistence/cross-function interactions.
- Include a **“Difficulty & Fairness”** subsection in the Description explaining why it’s challenging yet fair.
- Do **not** claim that tests were run X times; encode difficulty in spec and tests.

---

## Category Rules

### A) Bug Fix
- Keep **public API unchanged**; base code is runnable but buggy.
- If a pipeline exists, the order must be **merge → transform (defaults, coercions, transforms) → validate**.
- `float` validations accept `int` values.
- Unknown fields are preserved unless expressly covered by the schema.
- Error messages and precedence must be **explicit** and matched **exactly**.
- Nested field paths use **dot notation**.

### B) Completion
- Pin non-stdlib deps (e.g., `pandas==2.1.4`, `numpy==1.26.x`, `openpyxl==3.1.x`) and use only those.
- CLI strictly via `sys.argv` (no argparse).
- **API returns** strings **without trailing newline**; **CLI prints** add **one** trailing newline.
- Define error precedence and assert it. Numeric outputs rounded to **2 decimals**; sample standard deviation uses **ddof=1**.
- Persistence and cross-call behavior (if any) must be specified and tested.

---

## Domain Canons (from our three exemplars)

### 1) Configuration Processor (Bug Fix)
**Required pipeline:** `merge → transform → validate`.

**Merging**
- Deep merge for dictionaries; later files override earlier ones.
- Lists are **replaced** (not concatenated).
- Unknown fields preserved.

**Transforms**
- Defaults applied for missing fields that declare `default`.
- Type coercions:
  - `"123" → 123` (int), `"-45" → -45`
  - `"15.5" → 15.5` (float)
  - String booleans: `"true"`, `"1"`, `"yes"`, `"on"` → `True`; other strings → `False` (case-insensitive)
  - Any type → string for `type: "string"` via `str(value)`
- String transforms: `"uppercase"`, `"lowercase"`, `"strip"`
- Numeric transform: `"abs"`

**Validation (after transform)**
- Types supported: `"string"`, `"integer"`, `"float"`, `"boolean"`, `"list"`, `"dict"`
- Required fields; min/max for numerics; min_length/max_length for strings/lists; `allowed_values`.
- Nested schemas via `nested_schema` for dicts.
- **Type names** in messages: `str`, `int`, `float`, `bool`, `list`, `dict` (lowercase).
- **Dot paths** for nested fields (e.g., `database.host`).

**Exact validation messages**
- Missing: `Required field '{path}' is missing`
- Type: `Field '{path}' must be {expected_type}, got {actual_type}`
- Min value: `Field '{path}' value {value} is below minimum {min_value}`
- Max value: `Field '{path}' value {value} is above maximum {max_value}`
- Min length: `Field '{path}' length {length} is below minimum {min_length}`
- Max length: `Field '{path}' length {length} is above maximum {max_length}`
- Allowed: `Field '{path}' value '{value}' not in allowed values {allowed_values}`

**INI parsing**
- Booleans: `true/false` (case-insensitive).
- Numbers: if token contains `.`, parse as float; else try int; fallback to raw string.

**Process-all error raising**
- On validation failure: raise `ConfigurationError("Configuration validation failed: {err1}; {err2}; ...")`.

---

### 2) Data Analyzer CLI (Completion; Pandas)
**Allowed deps**: `pandas==2.1.4+`, `numpy==1.26.x`, `openpyxl==3.1.x` (for Excel export).

**CLI commands**
- `load <csv_file> <dataset_name>`
- `describe <dataset_name>`
- `compare <dataset1> <dataset2> <column_name>`
- `export <dataset_name> <output_file>`
- `filter <dataset> <column> <operator> <value> <new_dataset>`
- `merge <dataset1> <dataset2> <column> <new_dataset>`

**File format validation**
- Must end with `.csv`.
- Must be readable by `pd.read_csv`.
- Must have proper headers (not a first row that is all numeric).
- Empty DataFrame or parsing error → `"ERROR: invalid file format"`.

**Persistence**
- On `load`, save to `datasets/<name>.pkl` and cache in memory.
- Other commands may load from cache or from the pickle if not cached.

**Type inference priority**
1. **Numeric** if all tokens are numeric strings (e.g., `"1"`, `"2.5"`).
2. **Date** if tokens match common forms: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD-MM-YYYY`, and month-name forms like `"Jan 1, 2023"`.
3. Otherwise **text** (`object`).
4. Ambiguous like `"2023"` → numeric (priority over date).

**Missing values**
- Empty strings are missing.
- Numeric columns: if a mode exists with frequency ≥2, fill with the **numeric smallest** among the modes; otherwise fill with **median**.
- Text columns: fill with mode; ties choose **lexicographically smallest** token.

**Describe/Compare output**
- Numeric stats: count, mean, std, min, 25%, 50%, 75%, max (round to **2 decimals**, std is **sample** ddof=1).
- Text output: `count`, `unique`, `top`, `freq`.
- Date columns: report like text (compute manually) and show dtype `datetime64[ns]`.

**Filter**
- Operators: `> < >= <= == != contains not_contains`
- Numeric: only comparison/equals ops; text: `contains`/`not_contains`; date: comparisons with **strict `YYYY-MM-DD`** input.
- `contains` matching is case-insensitive.
- Invalid operator for column type → `"ERROR: invalid operator"`.
- Value parse failures → `"ERROR: invalid value"`.
- Empty result → `"ERROR: operation failed"`.

**Merge**
- Inner join on the given column; both must have that column.
- Column types must be compatible (both numeric or both text); otherwise `"ERROR: operation failed"`.
- Duplicate non-key columns adopt pandas defaults (`_x`, `_y`).

**Error precedence (check in this order)**
1. `"ERROR: file not found"`
2. `"ERROR: invalid file format"`
3. `"ERROR: dataset not found"`
4. `"ERROR: column not found"`
5. `"ERROR: invalid operator"`
6. `"ERROR: invalid value"`
7. `"ERROR: operation failed"`

**CLI vs API newline**
- API methods return strings **without** trailing newline; CLI prints add **one** trailing newline.

---

### 3) Raft Log Validator (Bug Fix)
**Log entry**
```python
{"term": int, "index": int, "data": Any, "timestamp": float}
```
Indexing starts at **1**.

**append_entry(term, data, prev_log_index=None, prev_log_term=None) → dict**
- Reject if `term < current_term` → `"Term is lower than current term"`.
- If `term > current_term`, set `current_term = term` and `voted_for = None`.
- Previous-log checks:
  - If both provided and `prev_log_index` is out of range (negative or > len), return `"Previous log index out of range"`.
  - Sentinel `(prev_log_index=0, prev_log_term=0)` is accepted.
  - If existing, require `log[prev_log_index-1].term == prev_log_term`, else `"Previous log entry mismatch"`.
- New index:
  - If `prev_log_index` is provided, `new_index = prev_log_index + 1`; else `len(log) + 1`.
- Conflict:
  - If `new_index` already exists and its term differs:
    - If `new_index > commit_index`, truncate `log` to `new_index-1` then append.
    - Else **fail** `"Cannot overwrite committed entries"`.
- On success: `{"success": True, "current_term": current_term, "log_index": new_index, "message": "Entry appended successfully"}`.

**commit_entries(leader_commit_index) → dict**
- Fail if `leader_commit_index > len(log)`.
- Never decrease commit index; if lower, return success with `committed_count=0`.
- Validate no gaps: all indices `1..leader_commit_index` must exist.
- On success, set commit index; return `{"success": True, "committed_count": delta, "commit_index": new_commit_index}`.

**advance_term(new_term) → bool**
- Only advance on strictly higher term; set `voted_for = None` on advance.

**get_term_for_index(i) → int**
- `i == 0 → 0`; invalid/non-existent → `-1`; else entry term.

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
- Terms strictly monotonic.
- Committed entries are never truncated or overwritten.
- If two logs share an entry at (index, term), all preceding entries are identical.

---
