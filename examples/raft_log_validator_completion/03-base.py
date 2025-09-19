import time
from typing import Any, Dict, List, Optional


class RaftLogValidator:
    """
    Implement a Raft log validator that satisfies the tests in 02-tests.py.
    Fill in all methods. Follow the exact return shapes and messages.
    """
    def __init__(self, node_id: str, initial_term: int = 0):
        self.node_id = node_id
        self.current_term = initial_term
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []
        self.commit_index = 0

    def append_entry(self, term: int, entry_data: Any, prev_log_index: Optional[int] = None, 
                    prev_log_term: Optional[int] = None) -> Dict[str, Any]:
        """Append a new entry after validating Raft safety rules.
        Return dict: {success, current_term, log_index, message}.
        """
        raise NotImplementedError

    def commit_entries(self, leader_commit_index: int) -> Dict[str, Any]:
        """Advance the commit index safely.
        Return dict: {success, committed_count, commit_index}.
        """
        raise NotImplementedError

    def get_log_info(self) -> Dict[str, Any]:
        """Return node/log metrics with exact keys & semantics required by tests."""
        raise NotImplementedError

    def advance_term(self, new_term: int) -> bool:
        """Advance to a strictly higher term and reset voted_for."""
        raise NotImplementedError

    def get_term_for_index(self, log_index: int) -> int:
        """Return term for 1-based index, 0 for index 0, -1 otherwise."""
        raise NotImplementedError