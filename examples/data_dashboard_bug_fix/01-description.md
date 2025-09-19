# Data Analysis Dashboard — Bug Fix Edition

You are given a **buggy implementation** of a command-line data analysis tool (`DataAnalyzer`) that loads and analyzes CSV datasets.
Your job is to **identify and fix the bugs** so the implementation satisfies the spec and passes the test suite.

## CLI

```
python solution.py <command> [arguments]
```

Commands:

1. `load <csv_file> <dataset_name>` — Load a CSV file and store it with a name
2. `describe <dataset_name>` — Show statistical summary of the dataset
3. `compare <dataset1> <dataset2> <column_name>` — Compare a numeric column between datasets
4. `export <dataset_name> <output_file>` — Export dataset to Excel (.xlsx)
5. `filter <dataset_name> <column_name> <operator> <value> <new_dataset_name>` — Filter and save as new dataset
6. `merge <dataset1> <dataset2> <column_name> <new_dataset_name>` — Inner-merge on a column

## Requirements (must-haves)

**File format validation**
- Files must have `.csv` extension.
- Files must be readable by `pandas.read_csv()` and not empty.
- CSV must have **proper headers**: if the first row is purely numeric (i.e., all cells are numbers), treat as `"ERROR: invalid file format"`.
- If invalid, return `"ERROR: invalid file format"`.

**Type inference & cleaning**
- Empty strings `""` are treated as missing values.
- Detect and convert **date columns** automatically (supported formats: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD-MM-YYYY`, Month-name formats like `Jan 1, 2023`).  
- Type inference priority (per column):
  1) All values numeric-like → convert to numeric
  2) Date-like → convert to datetime
  3) Otherwise object (text)
  4) For ambiguous (e.g., `"2023"`), numeric wins over date.

**Missing values filling**
- For **numeric** columns:  
  If a mode exists with max frequency ≥ 2, fill missing with the smallest numeric mode; otherwise fill with the **median**.
- For **text** columns: fill missing (incl. empty strings) with **mode** (lexicographically smallest when multiple).

**Data validation**
- Numeric columns must contain only numbers (or missing placeholders before cleaning).
- Text columns can contain any string.
- Mixed-type should be coerced to text.
- Date columns must be `datetime64[ns]`.

**Persistence**
- Create a `datasets/` directory.
- On `load`, save the dataset to `datasets/<dataset_name>.pkl` and cache in memory.
- Other commands should lazily load from `datasets/<dataset_name>.pkl` if not in memory.

**Describe output**
- For numeric columns: `count, mean, std, min, 25%, 50%, 75%, max` (rounded to 2 decimals).
- For text and date columns (treated text-style for summary): `count, unique, top, freq`.
- Format:
  ```
  Dataset: <name>
  Shape: <rows> rows, <columns> columns
  Columns:
  - <col>: <dtype> (<stats>)
  ```

**Compare**
- Only for **numeric** columns; otherwise `"ERROR: column not found"`.
- Output:
  ```
  Comparison: <column> between <dataset1> and <dataset2>
  <dataset1>: mean=<v> std=<v> count=<n>
  <dataset2>: mean=<v> std=<v> count=<n>
  Difference: <mean1 - mean2>
  ```
  (all numeric rounded to 2 decimals)

**Export**
- Write to Excel: `OK: dataset <name> exported to <output_file>`.

**Filter**
- Operators: `> < >= <= == != contains not_contains`
- Numeric columns support: `> < >= <= == !=` with numeric value
- Text columns support: `contains not_contains` (case-insensitive)
- Date columns accept date values (prefer `YYYY-MM-DD`)
- Error precedence:
  1) `"ERROR: dataset not found"`
  2) `"ERROR: column not found"`
  3) `"ERROR: invalid operator"`
  4) `"ERROR: invalid value"`
  5) `"ERROR: operation failed"` (e.g., empty result)

**Merge**
- Inner join on the given column.
- Both datasets must contain the column and the column types must be compatible (both numeric or both text).
- Handle duplicate column names with pandas default suffixes (`_x`, `_y`).
- On no common values or incompatibility, `"ERROR: operation failed"`.

**Universal error messages** (exact strings):
- `ERROR: dataset not found`
- `ERROR: column not found`
- `ERROR: file not found`
- `ERROR: invalid file format`
- `ERROR: invalid operator`
- `ERROR: invalid value`
- `ERROR: operation failed`

**CLI usage text is non-normative** (tests only check the exact OK/ERROR outputs).

---

## What you get

- `03-base.py` — the **buggy** implementation you must fix (rename to `solution.py` when you work).  
- Your fixes should make all tests in `02-tests.py` pass.  
- `04-solution.py` is a **reference** implementation for maintainers.

Good luck — keep the pass rate fair but achievable!
