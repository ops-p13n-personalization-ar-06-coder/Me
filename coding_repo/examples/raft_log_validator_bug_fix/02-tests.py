import pytest
import time
from typing import Any
from solution import RaftLogValidator


class TestRaftLogValidator:
    def test_init_basic(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        info = validator.get_log_info()
        assert info["node_id"] == "node_1"
        assert info["current_term"] == 1
        assert info["log_length"] == 0
        assert info["commit_index"] == 0
        assert info["last_log_index"] == 0
        assert info["last_log_term"] == 0
        assert info["voted_for"] is None

    def test_init_default_term(self):
        validator = RaftLogValidator("node_2")
        info = validator.get_log_info()
        assert info["current_term"] == 0

    def test_append_entry_first_entry(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        result = validator.append_entry(term=1, entry_data={"operation": "set", "key": "x", "value": 10})
        assert result["success"] is True
        assert result["current_term"] == 1
        assert result["log_index"] == 1
        assert result["message"] == "Entry appended successfully"
        info = validator.get_log_info()
        assert info["log_length"] == 1
        assert info["last_log_index"] == 1
        assert info["last_log_term"] == 1

    def test_append_entry_sequential(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        result1 = validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        assert result1["success"] is True
        assert result1["log_index"] == 1
        result2 = validator.append_entry(term=1, entry_data={"cmd": "set", "key": "b", "value": 2})
        assert result2["success"] is True
        assert result2["log_index"] == 2
        info = validator.get_log_info()
        assert info["log_length"] == 2
        assert info["last_log_index"] == 2
        assert info["last_log_term"] == 1

    def test_append_entry_with_prev_log_validation_success(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        result = validator.append_entry(
            term=1, 
            entry_data={"cmd": "set", "key": "b", "value": 2},
            prev_log_index=1,
            prev_log_term=1
        )
        assert result["success"] is True
        assert result["log_index"] == 2
        assert result["message"] == "Entry appended successfully"

    def test_append_entry_prev_log_mismatch_term(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        result = validator.append_entry(
            term=1,
            entry_data={"cmd": "set", "key": "b", "value": 2},
            prev_log_index=1,
            prev_log_term=2
        )
        assert result["success"] is False
        assert result["log_index"] == -1
        assert result["message"] == "Previous log entry mismatch"

    def test_append_entry_prev_log_index_out_of_range(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        result = validator.append_entry(
            term=1,
            entry_data={"cmd": "set", "key": "a", "value": 1},
            prev_log_index=5,
            prev_log_term=1
        )
        assert result["success"] is False
        assert result["log_index"] == -1
        assert result["message"] == "Previous log index out of range"

    def test_append_entry_lower_term_rejection(self):
        validator = RaftLogValidator("node_1", initial_term=2)
        result = validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        assert result["success"] is False
        assert result["current_term"] == 2
        assert result["log_index"] == -1
        assert result["message"] == "Term is lower than current term"

    def test_append_entry_term_advancement(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        result = validator.append_entry(term=3, entry_data={"cmd": "set", "key": "a", "value": 1})
        assert result["success"] is True
        assert result["current_term"] == 3
        assert result["log_index"] == 1
        assert result["message"] == "Entry appended successfully"
        info = validator.get_log_info()
        assert info["current_term"] == 3
        assert info["voted_for"] is None

    def test_append_entry_conflict_resolution(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "b", "value": 2})
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "c", "value": 3})
        validator.commit_entries(1)
        result = validator.append_entry(
            term=2,
            entry_data={"cmd": "delete", "key": "b"},
            prev_log_index=1,
            prev_log_term=1
        )
        assert result["success"] is True
        assert result["log_index"] == 2
        info = validator.get_log_info()
        assert info["log_length"] == 2
        assert info["last_log_term"] == 2

    def test_commit_entries_success(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "b", "value": 2})
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "c", "value": 3})
        result = validator.commit_entries(2)
        assert result["success"] is True
        assert result["committed_count"] == 2
        assert result["commit_index"] == 2
        info = validator.get_log_info()
        assert info["commit_index"] == 2

    def test_commit_entries_no_new_commits(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.commit_entries(1)
        result = validator.commit_entries(1)
        assert result["success"] is True
        assert result["committed_count"] == 0
        assert result["commit_index"] == 1

    def test_commit_entries_beyond_log_length(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        result = validator.commit_entries(5)
        assert result["success"] is False
        assert result["committed_count"] == 0
        assert result["commit_index"] == 0

    def test_commit_entries_never_decrease(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "b", "value": 2})
        validator.commit_entries(2)
        result = validator.commit_entries(1)
        assert result["success"] is True
        assert result["committed_count"] == 0
        assert result["commit_index"] == 2

    def test_advance_term_success(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.voted_for = "candidate_1"
        result = validator.advance_term(3)
        assert result is True
        info = validator.get_log_info()
        assert info["current_term"] == 3
        assert info["voted_for"] is None

    def test_advance_term_failure_not_higher(self):
        validator = RaftLogValidator("node_1", initial_term=3)
        result1 = validator.advance_term(3)
        assert result1 is False
        result2 = validator.advance_term(2)
        assert result2 is False
        info = validator.get_log_info()
        assert info["current_term"] == 3

    def test_get_term_for_index_valid_indices(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.advance_term(2)
        validator.append_entry(term=2, entry_data={"cmd": "set", "key": "b", "value": 2})
        assert validator.get_term_for_index(1) == 1
        assert validator.get_term_for_index(2) == 2

    def test_get_term_for_index_special_cases(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        assert validator.get_term_for_index(0) == 0
        assert validator.get_term_for_index(-1) == -1
        assert validator.get_term_for_index(5) == -1

    def test_log_entry_format(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"operation": "set", "key": "x", "value": 10})
        assert validator.get_term_for_index(1) == 1
        info = validator.get_log_info()
        assert info["last_log_index"] == 1
        assert info["last_log_term"] == 1

    def test_complex_scenario_leader_change(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "b", "value": 2})
        validator.commit_entries(1)
        validator.advance_term(2)
        result = validator.append_entry(
            term=2,
            entry_data={"cmd": "delete", "key": "b"},
            prev_log_index=1,
            prev_log_term=1
        )
        assert result["success"] is True
        assert result["log_index"] == 2
        info = validator.get_log_info()
        assert info["current_term"] == 2
        assert info["log_length"] == 2
        assert info["commit_index"] == 1
        assert info["last_log_term"] == 2

    def test_committed_entries_safety(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "b", "value": 2})
        validator.commit_entries(2)
        result = validator.append_entry(
            term=2,
            entry_data={"cmd": "delete", "key": "different"},
            prev_log_index=1,
            prev_log_term=1
        )
        assert result["success"] is False
        assert result["message"] == "Cannot overwrite committed entries"
        info = validator.get_log_info()
        assert info["commit_index"] == 2
        assert info["log_length"] == 2

    def test_monotonic_term_progression(self):
        validator = RaftLogValidator("node_1", initial_term=1)
        validator.append_entry(term=1, entry_data={"cmd": "set", "key": "a", "value": 1})
        validator.advance_term(2)
        validator.append_entry(term=2, entry_data={"cmd": "set", "key": "b", "value": 2})
        validator.advance_term(4)
        validator.append_entry(term=4, entry_data={"cmd": "set", "key": "c", "value": 3})
        assert validator.get_term_for_index(1) == 1
        assert validator.get_term_for_index(2) == 2
        assert validator.get_term_for_index(3) == 4
        info = validator.get_log_info()
        assert info["current_term"] == 4

    def test_log_consistency_property(self):
        validator1 = RaftLogValidator("node_1", initial_term=1)
        validator2 = RaftLogValidator("node_2", initial_term=1)
        entries = [
            (1, {"cmd": "set", "key": "a", "value": 1}),
            (1, {"cmd": "set", "key": "b", "value": 2}),
            (2, {"cmd": "delete", "key": "a"}),
        ]
        for term, data in entries:
            if term > validator1.get_log_info()["current_term"]:
                validator1.advance_term(term)
                validator2.advance_term(term)
            validator1.append_entry(term, data)
            validator2.append_entry(term, data)
        info1 = validator1.get_log_info()
        info2 = validator2.get_log_info()
        assert info1["current_term"] == info2["current_term"]
        assert info1["log_length"] == info2["log_length"]
        assert info1["last_log_index"] == info2["last_log_index"]
        assert info1["last_log_term"] == info2["last_log_term"]

    def test_boundary_conditions(self):
        validator = RaftLogValidator("node_1", initial_term=0)
        result = validator.append_entry(term=0, entry_data={"cmd": "init"})
        assert result["success"] is True
        assert validator.advance_term(1) is True
        assert validator.advance_term(1000000) is True
        info = validator.get_log_info()
        assert info["current_term"] == 1000000