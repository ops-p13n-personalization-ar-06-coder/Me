# Raft Log Validator — Completion

Implement a Raft consensus log entry validator that manages distributed log replication with term validation, log consistency checks, and safe commit progression. You are given tests and a starter (`03-base.py`). Write the full implementation so that **all tests pass**.

## Files
- `03-base.py` — Starter skeleton (copy/rename to `solution.py` and implement)
- `02-tests.py` — Unit tests (authoritative spec)
- `04-solution.py` — Reference solution (for maintainers; do not look during solving)

## API Interface

```python
class RaftLogValidator:
    def __init__(self, node_id: str, initial_term: int = 0)
    def append_entry(self, term: int, entry_data: Any, prev_log_index: int = None, prev_log_term: int = None) -> dict
    def commit_entries(self, leader_commit_index: int) -> dict
    def get_log_info(self) -> dict
    def advance_term(self, new_term: int) -> bool
    def get_term_for_index(self, log_index: int) -> int
```

## Requirements Summary

### 1) Core Log Operations — `append_entry`
Return dict with keys: `success`, `current_term`, `log_index`, `message`.

Accept if:
- Term >= current term (advance `current_term` if higher, reset `voted_for=None`)
- If `prev_log_index` & `prev_log_term` provided, they must match current log
- New entry index is `prev_log_index + 1` (if provided) or `len(log) + 1`
- On conflict at the new index (different term): truncate from that index **only if all are uncommitted**, else reject `"Cannot overwrite committed entries"`

Reject if:
- Lower term → `"Term is lower than current term"`
- `prev_log_index` out of range → `"Previous log index out of range"`
- `prev_log_term` mismatch → `"Previous log entry mismatch"`

### 2) Term Management — `advance_term`
- Only advance to strictly higher term; reset `voted_for=None`
- Return `True` if advanced, else `False`

### 3) Commit Management — `commit_entries`
- Never commit beyond `len(log)`; never decrease commit index
- Validate there are no gaps
- Return `{"success": True/False, "committed_count": int, "commit_index": int}`

### 4) Info & Query
- `get_log_info()` returns **exactly**:
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
- `get_term_for_index(0) == 0`; invalid indices → `-1`

### Properties
- Term numbers strictly monotonic
- If two logs share index & term, all preceding entries are identical
- Committed entries are never truncated

## Log Entry Format
```python
{
    "term": int,
    "index": int,
    "data": Any,
    "timestamp": float
}
```

## How to Run
1. Copy `03-base.py` → `solution.py` and implement.
2. Run tests: `pytest -q 02-tests.py`