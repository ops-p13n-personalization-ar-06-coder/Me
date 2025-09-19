import time
from typing import Any, Dict, List, Optional


class RaftLogValidator:
    """
    A buggy implementation of a Raft consensus algorithm log entry validator.
    This implementation contains several subtle bugs that need to be identified and fixed.
    """

    def __init__(self, node_id: str, initial_term: int = 0):
        self.node_id = node_id
        self.current_term = initial_term
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []
        self.commit_index = 0

    def append_entry(self, term: int, entry_data: Any, prev_log_index: Optional[int] = None, 
                    prev_log_term: Optional[int] = None) -> Dict[str, Any]:
        if term <= self.current_term:
            return {
                "success": False,
                "current_term": self.current_term,
                "log_index": -1,
                "message": "Term is lower than current term"
            }

        if term > self.current_term:
            self.current_term = term

        if prev_log_index is not None and prev_log_term is not None:
            if prev_log_index <= 0 or prev_log_index > len(self.log):
                return {
                    "success": False,
                    "current_term": self.current_term,
                    "log_index": -1,
                    "message": "Previous log index out of range"
                }

            expected_term = self.log[prev_log_index - 1]["term"]

            if expected_term != prev_log_term:
                return {
                    "success": False,
                    "current_term": self.current_term,
                    "log_index": -1,
                    "message": "Previous log entry mismatch"
                }

        new_index = len(self.log) + 1

        new_entry = {
            "term": term,
            "index": new_index,
            "data": entry_data,
            "timestamp": time.time()
        }

        self.log.append(new_entry)

        return {
            "success": True,
            "current_term": self.current_term,
            "log_index": new_index,
            "message": "Entry appended successfully"
        }

    def commit_entries(self, leader_commit_index: int) -> Dict[str, Any]:
        if leader_commit_index < self.commit_index:
            return {
                "success": True,
                "committed_count": 0,
                "commit_index": self.commit_index
            }

        old_commit_index = self.commit_index
        self.commit_index = leader_commit_index
        newly_committed = self.commit_index - old_commit_index

        return {
            "success": True,
            "committed_count": newly_committed,
            "commit_index": self.commit_index
        }

    def get_log_info(self) -> Dict[str, Any]:
        if len(self.log) == 0:
            last_log_index = -1
            last_log_term = -1
        else:
            last_log_index = len(self.log)
            last_log_term = self.log[-1]["term"]

        return {
            "node_id": self.node_id,
            "current_term": self.current_term,
            "log_length": len(self.log),
            "commit_index": self.commit_index,
            "last_log_index": last_log_index,
            "last_log_term": last_log_term,
            "voted_for": self.voted_for
        }

    def advance_term(self, new_term: int) -> bool:
        if new_term >= self.current_term:
            self.current_term = new_term
            self.voted_for = None
            return True
        return False

    def get_term_for_index(self, log_index: int) -> int:
        if log_index == 0:
            return 0

        if log_index < 0 or log_index >= len(self.log):
            return -1

        return self.log[log_index - 1]["term"]