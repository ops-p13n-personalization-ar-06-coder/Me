# Raft Log Validator — Bug Fix

You are given a buggy implementation of a Raft consensus algorithm log entry validator that manages distributed log replication with term validation and log consistency checks. The existing implementation contains several subtle bugs that cause log corruption, inconsistent state transitions, and violation of Raft safety properties. Identify and fix all bugs in the provided implementation to make the distributed log system pass the comprehensive test suite.

## Files
- `03-base.py` — Buggy starter code (rename to `solution.py` when running tests)
- `02-tests.py` — Unit tests you must pass
- `04-solution.py` — Reference solution (for maintainers)

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

## Requirements

### 1) Core Log Operations

**`append_entry(term, entry_data, prev_log_index=None, prev_log_term=None)`**

Returns: `{"success": bool, "current_term": int, "log_index": int, "message": str}`

Success Cases:
- Entry appended successfully: `{"success": True, "current_term": current_term, "log_index": new_index, "message": "Entry appended successfully"}`
- Term updated and entry appended: `{"success": True, "current_term": new_term, "log_index": new_index, "message": "Entry appended successfully"}`

Failure Cases:
- Term too low: `{"success": False, "current_term": current_term, "log_index": -1, "message": "Term is lower than current term"}`
- Previous log mismatch: `{"success": False, "current_term": current_term, "log_index": -1, "message": "Previous log entry mismatch"}`
- Previous index out of range: `{"success": False, "current_term": current_term, "log_index": -1, "message": "Previous log index out of range"}`
- Cannot overwrite committed entries: `{"success": False, "current_term": current_term, "log_index": -1, "message": "Cannot overwrite committed entries"}`

Behavior:
- Must reject entries from lower terms than current term
- Must validate previous log entry consistency if `prev_log_index` and `prev_log_term` are provided
- Must auto-increment log indices starting from 1
- Must update current term if entry term is higher than current term and reset `voted_for` to `None`
- If `prev_log_index` points to a non-existent entry, must reject with "Previous log index out of range"
- If `prev_log_index` exists but `prev_log_term` doesn't match, must reject with "Previous log entry mismatch"
- If an existing entry at the new log index conflicts with the new entry (same index, different terms), must truncate the existing entry and all subsequent entries **only if they are not committed**, before appending the new entry

### 2) Term Management and State

**`advance_term(new_term)`**

Returns: `bool`
- `True` if term was advanced to `new_term`
- `False` if `new_term` is not higher than current term

Behavior:
- Must only advance to higher terms
- Must reset `voted_for` to `None` when advancing terms
- Must maintain monotonic term progression

**`get_term_for_index(log_index)`**

Returns: `int`
- Term number for valid indices (1 to log length)
- `0` for `log_index` 0 (special case)
- `-1` for other invalid or non-existent indices

### 3) Commit Management

**`commit_entries(leader_commit_index)`**

Returns: `{"success": bool, "committed_count": int, "commit_index": int}`

Success Cases:
- Entries committed: `{"success": True, "committed_count": num_newly_committed, "commit_index": new_commit_index}`
- No new commits: `{"success": True, "committed_count": 0, "commit_index": current_commit_index}`

Failure Cases:
- Commit index too high: `{"success": False, "committed_count": 0, "commit_index": current_commit_index}`
- Log gaps detected: `{"success": False, "committed_count": 0, "commit_index": current_commit_index}`

Behavior:
- Must never commit entries beyond current log length
- Must never decrease commit index
- Must ensure committed entries are never truncated
- Must validate that all entries up to commit index exist without gaps

### 4) Information and Metrics

**`get_log_info()`** must return exactly:
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

Special case: if the log is empty, `last_log_index=0` and `last_log_term=0`.

## Properties
- Term numbers must be strictly monotonic
- New entries are only appended to the log (unless truncating conflicts)
- If two logs contain an entry with the same index and term, then all preceding entries are identical
- If a log entry is committed, it will never be overwritten or deleted
- Committed entries are never truncated from the log

## Log Entry Format
```python
{
    "term": int,        # Term when entry was created
    "index": int,       # Log position (starts from 1)
    "data": Any,        # Arbitrary entry data
    "timestamp": float  # Creation timestamp
}
```

## Example
```python
import time
validator = RaftLogValidator("node_1", initial_term=1)
result = validator.append_entry(term=1, entry_data={"operation": "set", "key": "x", "value": 10})
# {"success": True, "current_term": 1, "log_index": 1, "message": "Entry appended successfully"}

result = validator.append_entry(term=1, entry_data={"cmd": "delete", "key": "y"}, prev_log_index=1, prev_log_term=1)
# {"success": True, "current_term": 1, "log_index": 2, "message": "Entry appended successfully"}

result = validator.commit_entries(leader_commit_index=2)
# {"success": True, "committed_count": 2, "commit_index": 2}

advanced = validator.advance_term(new_term=2)
# True

info = validator.get_log_info()
# {"node_id": "node_1", "current_term": 2, "log_length": 2, "commit_index": 2, "last_log_index": 2, "last_log_term": 1, "voted_for": None}
```

## How to Run
1. Rename `03-base.py` to `solution.py`.
2. Run tests: `pytest -q 02-tests.py`
3. Fix bugs in `solution.py` until all tests pass.