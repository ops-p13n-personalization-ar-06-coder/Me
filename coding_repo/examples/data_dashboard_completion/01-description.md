# Data Analysis Dashboard — Completion Task

Create a command-line tool that loads and analyzes CSV datasets.

## CLI

```
python solution.py <command> [arguments]
```

### Commands

1. **load `<csv_file>` `<dataset_name>`**  
   Load a CSV file and store it with a name.

2. **describe `<dataset_name>`**  
   Show statistical summary of the dataset.

3. **compare `<dataset1>` `<dataset2>` `<column_name>`**  
   Compare a specific **numeric** column between two datasets.

4. **export `<dataset_name>` `<output_file>`**  
   Export dataset to Excel format.

5. **filter `<dataset_name>` `<column_name>` `<operator>` `<value>` `<new_dataset_name>`**  
   Filter dataset based on column condition and save as new dataset.

6. **merge `<dataset1>` `<dataset2>` `<column_name>` `<new_dataset_name>`**  
   Merge two datasets on a common column and save as new dataset.

---

## Requirements

### File format validation
- Files **must** have `.csv` extension.
- Files must be readable by `pandas.read_csv()`.
- Files must have headers.
- If the first row contains only numeric values (i.e., no proper headers), treat it as **`ERROR: invalid file format`**.
- If `read_csv` raises or results in an empty DataFrame, return **`ERROR: invalid file format`**.

### Missing values
- Empty strings (`""`) are treated as missing values.
- For **numeric** columns: if there is a repeated numeric **mode** (max frequency ≥ 2), fill missing with the numeric mode (if multiple modes, choose the numerically smallest); otherwise fill with the **median**.
- For **text** columns: fill with **mode** (if ties, lexicographically smallest).
- For **date** columns: fill with **median** (midpoint) of the datetime column.

### Type inference priority (in order)
1. If all values in a column are numeric strings (e.g., `"1"`, `"2.5"`, `"10"`), convert to **numeric**.
2. If values match common date formats (**YYYY-MM-DD**, **MM/DD/YYYY**, **DD-MM-YYYY**, month-name like `"Jan 1, 2023"`), convert to **datetime64[ns]**.
3. Otherwise, treat as **text** (`object`).
4. Prioritize **numeric** over **date** for ambiguous values (e.g., `"2023"` should be numeric).

### Persistence
- Save loaded datasets as pickle files inside a local **`datasets/`** directory as `datasets/<dataset_name>.pkl`.
- The **load** command saves datasets to disk and memory.
- Other commands load datasets from memory if present, or from disk if not (implementation-defined cache is fine).

### Operators for `filter`
- Supported: `>`, `<`, `>=`, `<=`, `==`, `!=`, `contains`, `not_contains`.
- **Numeric** columns: only the comparison/equality operators (no `contains`).
- **Text** columns: use `contains` / `not_contains` (case-insensitive).
- **Date** columns: comparison/equality with a value parseable by pandas (prefer `YYYY-MM-DD`).

### Merge
- Inner join on the specified column.
- Both datasets must contain the column.
- Types for the join column must be **compatible** (both numeric or both text).
- If there are duplicate non-join columns across datasets, rely on pandas default suffixing (`_x`, `_y`).

### Describe
- For numeric columns: report `count, mean, std, min, 25%, 50%, 75%, max` (rounded to 2 decimals).
- For text columns: report `count, unique, top, freq`.
- For date columns: report in the text style: `count, unique, top, freq` (compute manually).

### Error messages (exact text)
- `ERROR: dataset not found`
- `ERROR: column not found`
- `ERROR: file not found`
- `ERROR: invalid file format`
- `ERROR: invalid operator`
- `ERROR: invalid value`
- `ERROR: operation failed`

**Error precedence (check in this order):**
1. File not found
2. Invalid file format
3. Dataset not found
4. Column not found
5. Invalid operator
6. Invalid value
7. Operation failed

> Note: For the **compare** command, if the specified column exists but is not numeric, return `ERROR: column not found`.

### Output formats

**load**
```
OK: dataset <name> loaded with <rows> rows
```

**describe**
```
Dataset: <name>
Shape: <rows> rows, <columns> columns
Columns:
- <column>: <dtype> (count=<...>, ...)
```

**compare**
```
Comparison: <column> between <dataset1> and <dataset2>
<dataset1>: mean=<value> std=<value> count=<value>
<dataset2>: mean=<value> std=<value> count=<value>
Difference: <value>
```

**export**
```
OK: dataset <name> exported to <output_file>
```

**filter**
```
OK: dataset <new_name> created with <rows> rows
```

**merge**
```
OK: dataset <new_name> created with <rows> rows
```

---

## Implementation Guidelines

- Use only standard Python and **pandas 2.1.4+**.
- Follow pandas defaults for duplicate column naming and dtype inference.
- Use `pd.to_datetime(..., errors="coerce")` to detect supported date formats.
- Ensure numeric-vs-date precedence ("2023" should be numeric).
- Round numeric outputs to **2 decimals** in printed summaries.
- Keep CLI help/usage texts non-normative (tests do not assert them).

---

## Testing

Run the tests with:
```
pytest 02-tests.py -q
```

The tests import `solution` as `sol`. Your working file during evaluation should be named **`solution.py`**. This pack includes:
- `03-base.py` — starter skeleton to rename to `solution.py` when solving.
- `04-solution.py` — a reference solution (for maintainers).
