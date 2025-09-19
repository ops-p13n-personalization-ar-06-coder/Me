import os
import csv
import pandas as pd
import numpy as np
import pytest
import tempfile
from pathlib import Path
import pickle
import sys

import solution as sol

def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def test_load_basic(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["Bob", 30, 92.0], ["Charlie", "", 78.5]])
    
    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")
    
    assert result == "OK: dataset test_data loaded with 3 rows"
    assert "test_data" in analyzer.datasets
    assert len(analyzer.datasets["test_data"]) == 3

def test_load_missing_values_handling(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["", 30, 92.0], ["Charlie", 35, ""]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    df = analyzer.datasets["test_data"]
    assert df["name"].isna().sum() == 0
    assert df["age"].isna().sum() == 0
    assert df["score"].isna().sum() == 0
    
    assert df["age"].tolist() == [25, 30, 35]
    assert df["score"].tolist() == [85.5, 92.0, 88.75]
    assert df["name"].tolist() == ["Alice", "Alice", "Charlie"]

def test_load_errors(tmp_path):
    analyzer = sol.DataAnalyzer()
    
    result = analyzer.load("nonexistent.csv", "test")
    assert result == "ERROR: file not found"
    
    p = tmp_path / "data.txt"
    p.write_text("not a csv")
    result = analyzer.load(str(p), "test")
    assert result == "ERROR: invalid file format"
    
    p2 = tmp_path / "empty.csv"
    write_csv(p2, ["col1"], [])
    result = analyzer.load(str(p2), "test")
    assert result == "ERROR: invalid file format"

def test_load_no_header(tmp_path):
    analyzer = sol.DataAnalyzer()
    
    p = tmp_path / "no_header.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerows([[1, 2, 3], [4, 5, 6]])
    
    result = analyzer.load(str(p), "test")
    assert result == "ERROR: invalid file format"

def test_describe_basic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["Bob", 30, 92.0], ["Charlie", 35, 78.5]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    result = analyzer.describe("test_data")
    
    expected = """Dataset: test_data
Shape: 3 rows, 3 columns
Columns:
- name: object (count=3, unique=3, top=Alice, freq=1)
- age: int64 (count=3, mean=30.00, std=5.00, min=25.00, 25%=27.50, 50%=30.00, 75%=32.50, max=35.00)
- score: float64 (count=3, mean=85.33, std=6.75, min=78.50, 25%=82.00, 50%=85.50, 75%=88.75, max=92.00)"""
    
    assert result == expected

def test_describe_error():
    analyzer = sol.DataAnalyzer()
    result = analyzer.describe("nonexistent")
    assert result == "ERROR: dataset not found"

def test_compare_numeric(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["score"], [[85.5], [92.0], [78.5]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["score"], [[88.0], [95.0], [82.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "data1")
    analyzer.load(str(p2), "data2")
    
    result = analyzer.compare("data1", "data2", "score")
    
    expected = """Comparison: score between data1 and data2
data1: mean=85.33 std=6.75 count=3
data2: mean=88.33 std=6.51 count=3
Difference: -3.00"""
    
    assert result == expected

def test_compare_errors(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["score"], [[85.5]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "data1")
    
    result = analyzer.compare("nonexistent", "data1", "score")
    assert result == "ERROR: dataset not found"
    
    result = analyzer.compare("data1", "nonexistent", "score")
    assert result == "ERROR: dataset not found"
    
    result = analyzer.compare("data1", "data1", "nonexistent")
    assert result == "ERROR: column not found"

def test_compare_non_numeric(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["name", "age"], [["Alice", 25], ["Bob", 30]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["name", "age"], [["Charlie", 35], ["David", 40]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "data1")
    analyzer.load(str(p2), "data2")
    
    result = analyzer.compare("data1", "data2", "name")
    assert result == "ERROR: column not found"

def test_export_basic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age"], [["Alice", 25], ["Bob", 30]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    output_file = tmp_path / "output.xlsx"
    result = analyzer.export("test_data", str(output_file))
    
    assert result == f"OK: dataset test_data exported to {output_file}"
    assert output_file.exists()
    
    df = pd.read_excel(output_file)
    assert len(df) == 2
    assert list(df.columns) == ["name", "age"]

def test_export_error():
    analyzer = sol.DataAnalyzer()
    result = analyzer.export("nonexistent", "output.xlsx")
    assert result == "ERROR: dataset not found"

def test_persistence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age"], [["Alice", 25], ["Bob", 30]])
    
    analyzer1 = sol.DataAnalyzer()
    result = analyzer1.load(str(p), "test_data")
    assert result == "OK: dataset test_data loaded with 2 rows"
    
    pickle_file = tmp_path / "datasets" / "test_data.pkl"
    assert pickle_file.exists()
    
    analyzer2 = sol.DataAnalyzer()
    
    result = analyzer2.describe("test_data")
    expected = """Dataset: test_data
Shape: 2 rows, 2 columns
Columns:
- name: object (count=2, unique=2, top=Alice, freq=1)
- age: int64 (count=2, mean=27.50, std=3.54, min=25.00, 25%=26.25, 50%=27.50, 75%=28.75, max=30.00)"""
    assert result == expected
    
    result = analyzer2.compare("test_data", "test_data", "age")
    expected_compare = """Comparison: age between test_data and test_data
test_data: mean=27.50 std=3.54 count=2
test_data: mean=27.50 std=3.54 count=2
Difference: 0.00"""
    assert result == expected_compare
    
    output_file = tmp_path / "output.xlsx"
    result = analyzer2.export("test_data", str(output_file))
    assert result == f"OK: dataset test_data exported to {output_file}"
    assert output_file.exists()

def test_cli_commands(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age"], [["Alice", 25], ["Bob", 30]])
    
    import sys
    original_argv = sys.argv
    
    try:
        sys.argv = ["solution.py", "load", str(p), "test_data"]
        sol.main()
        captured = capsys.readouterr()
        assert captured.out == "OK: dataset test_data loaded with 2 rows\n"
        
        sys.argv = ["solution.py", "describe", "test_data"]
        sol.main()
        captured = capsys.readouterr()
        expected_describe = """Dataset: test_data
Shape: 2 rows, 2 columns
Columns:
- name: object (count=2, unique=2, top=Alice, freq=1)
- age: int64 (count=2, mean=27.50, std=3.54, min=25.00, 25%=26.25, 50%=27.50, 75%=28.75, max=30.00)
"""
        assert captured.out == expected_describe
        
        sys.argv = ["solution.py", "compare", "test_data", "test_data", "age"]
        sol.main()
        captured = capsys.readouterr()
        expected_compare = """Comparison: age between test_data and test_data
test_data: mean=27.50 std=3.54 count=2
test_data: mean=27.50 std=3.54 count=2
Difference: 0.00
"""
        assert captured.out == expected_compare
        
        output_file = tmp_path / "output.xlsx"
        sys.argv = ["solution.py", "export", "test_data", str(output_file)]
        sol.main()
        captured = capsys.readouterr()
        assert captured.out == f"OK: dataset test_data exported to {output_file}\n"
        assert output_file.exists()
    finally:
        sys.argv = original_argv

def test_filter_numeric_operations(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["Bob", 30, 92.0], ["Charlie", 35, 78.5]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    result = analyzer.filter("test_data", "age", ">", "30", "old_people")
    assert result == "OK: dataset old_people created with 1 rows"
    assert "old_people" in analyzer.datasets
    assert len(analyzer.datasets["old_people"]) == 1
    
    result = analyzer.filter("test_data", "age", ">=", "30", "adults")
    assert result == "OK: dataset adults created with 2 rows"
    assert "adults" in analyzer.datasets
    assert len(analyzer.datasets["adults"]) == 2
    
    result = analyzer.filter("test_data", "age", "==", "25", "alice_only")
    assert result == "OK: dataset alice_only created with 1 rows"
    assert "alice_only" in analyzer.datasets
    assert len(analyzer.datasets["alice_only"]) == 1
    
    result = analyzer.filter("test_data", "age", "!=", "25", "not_alice")
    assert result == "OK: dataset not_alice created with 2 rows"
    assert "not_alice" in analyzer.datasets
    assert len(analyzer.datasets["not_alice"]) == 2
    
    result = analyzer.filter("test_data", "age", "<", "30", "young_people")
    assert result == "OK: dataset young_people created with 1 rows"
    assert "young_people" in analyzer.datasets
    assert len(analyzer.datasets["young_people"]) == 1
    
    result = analyzer.filter("test_data", "age", "<=", "30", "young_or_30")
    assert result == "OK: dataset young_or_30 created with 2 rows"
    assert "young_or_30" in analyzer.datasets
    assert len(analyzer.datasets["young_or_30"]) == 2

def test_filter_text_operations(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["Bob", 30, 92.0], ["Charlie", 35, 78.5]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    result = analyzer.filter("test_data", "name", "contains", "a", "names_with_a")
    assert result == "OK: dataset names_with_a created with 2 rows"
    assert "names_with_a" in analyzer.datasets
    assert len(analyzer.datasets["names_with_a"]) == 2
    
    result = analyzer.filter("test_data", "name", "not_contains", "a", "names_without_a")
    assert result == "OK: dataset names_without_a created with 1 rows"
    assert "names_without_a" in analyzer.datasets
    assert len(analyzer.datasets["names_without_a"]) == 1
    
    result = analyzer.filter("test_data", "name", "contains", "alice", "names_with_alice_lower")
    assert result == "OK: dataset names_with_alice_lower created with 1 rows"
    assert "names_with_alice_lower" in analyzer.datasets
    assert len(analyzer.datasets["names_with_alice_lower"]) == 1
    
    result = analyzer.filter("test_data", "name", "contains", "ALICE", "names_with_alice_upper")
    assert result == "OK: dataset names_with_alice_upper created with 1 rows"
    assert "names_with_alice_upper" in analyzer.datasets
    assert len(analyzer.datasets["names_with_alice_upper"]) == 1
    
    result = analyzer.filter("test_data", "name", "not_contains", "ALICE", "names_without_alice_upper")
    assert result == "OK: dataset names_without_alice_upper created with 2 rows"
    assert "names_without_alice_upper" in analyzer.datasets
    assert len(analyzer.datasets["names_without_alice_upper"]) == 2

def test_filter_errors(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["Bob", 30, 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    result = analyzer.filter("nonexistent", "age", ">", "30", "new_dataset")
    assert result == "ERROR: dataset not found"
    
    result = analyzer.filter("test_data", "nonexistent", ">", "30", "new_dataset")
    assert result == "ERROR: column not found"
    
    result = analyzer.filter("test_data", "age", "invalid_op", "30", "new_dataset")
    assert result == "ERROR: invalid operator"
    
    result = analyzer.filter("test_data", "age", "contains", "30", "new_dataset")
    assert result == "ERROR: invalid operator"
    
    result = analyzer.filter("test_data", "age", ">", "invalid_value", "new_dataset")
    assert result == "ERROR: invalid value"
    
    result = analyzer.filter("test_data", "age", ">", "100", "new_dataset")
    assert result == "ERROR: operation failed"

def test_merge_basic(tmp_path):
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["id", "name", "age"], [["1", "Alice", 25], ["2", "Bob", 30]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["id", "score", "grade"], [["1", 85.5, "A"], ["2", 92.0, "A+"]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "dataset1")
    analyzer.load(str(p2), "dataset2")
    
    result = analyzer.merge("dataset1", "dataset2", "id", "merged_data")
    assert result == "OK: dataset merged_data created with 2 rows"
    
    merged_df = analyzer.datasets["merged_data"]
    assert len(merged_df) == 2
    assert "id" in merged_df.columns
    assert "name" in merged_df.columns
    assert "age" in merged_df.columns
    assert "score" in merged_df.columns
    assert "grade" in merged_df.columns

def test_merge_duplicate_columns(tmp_path):
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["id", "name", "value"], [["1", "Alice", 100], ["2", "Bob", 200]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["id", "name", "score"], [["1", "Alice", 85.5], ["2", "Bob", 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "dataset1")
    analyzer.load(str(p2), "dataset2")
    
    result = analyzer.merge("dataset1", "dataset2", "id", "merged_with_duplicates")
    assert result == "OK: dataset merged_with_duplicates created with 2 rows"
    
    merged_df = analyzer.datasets["merged_with_duplicates"]
    assert "name_x" in merged_df.columns
    assert "name_y" in merged_df.columns
    assert "value" in merged_df.columns
    assert "score" in merged_df.columns

def test_merge_errors(tmp_path):
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["id", "name"], [["1", "Alice"], ["2", "Bob"]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["id", "score"], [["1", 85.5], ["2", 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "dataset1")
    analyzer.load(str(p2), "dataset2")
    
    result = analyzer.merge("nonexistent", "dataset2", "id", "new_dataset")
    assert result == "ERROR: dataset not found"
    
    result = analyzer.merge("dataset1", "nonexistent", "id", "new_dataset")
    assert result == "ERROR: dataset not found"
    
    result = analyzer.merge("dataset1", "dataset2", "nonexistent", "new_dataset")
    assert result == "ERROR: column not found"

def test_merge_no_common_values(tmp_path):
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["id", "name"], [["1", "Alice"], ["2", "Bob"]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["id", "score"], [["3", 85.5], ["4", 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "dataset1")
    analyzer.load(str(p2), "dataset2")
    
    result = analyzer.merge("dataset1", "dataset2", "id", "new_dataset")
    assert result == "ERROR: operation failed"

def test_date_column_detection(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "date", "score"], [["Alice", "2023-01-01", 85.5], ["Bob", "2023-01-02", 92.0]])
    
    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")
    
    assert result == "OK: dataset test_data loaded with 2 rows"
    df = analyzer.datasets["test_data"]
    assert df["date"].dtype == "datetime64[ns]"

def test_describe_date_columns(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "date", "score"], [["Alice", "2023-01-01", 85.5], ["Bob", "2023-01-02", 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    result = analyzer.describe("test_data")
    assert "date: datetime64[ns]" in result
    assert "top=" in result
    assert "freq=" in result

def test_filter_date_operations(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "date", "score"], [["Alice", "2023-01-01", 85.5], ["Bob", "2023-01-02", 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    result = analyzer.filter("test_data", "date", ">", "2023-01-01", "later_dates")
    assert result == "OK: dataset later_dates created with 1 rows"
    assert "later_dates" in analyzer.datasets
    
    result = analyzer.filter("test_data", "date", "==", "2023-01-01", "specific_date")
    assert result == "OK: dataset specific_date created with 1 rows"
    assert "specific_date" in analyzer.datasets

def test_cli_filter_command(tmp_path, capsys):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["Bob", 30, 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")
    
    original_argv = sys.argv
    try:
        sys.argv = ["solution.py", "filter", "test_data", "age", ">", "25", "adults"]
        sol.main()
        captured = capsys.readouterr()
        assert captured.out == "OK: dataset adults created with 1 rows\n"
    finally:
        sys.argv = original_argv

def test_cli_merge_command(tmp_path, capsys):
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["id", "name"], [["1", "Alice"], ["2", "Bob"]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["id", "score"], [["1", 85.5], ["2", 92.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "dataset1")
    analyzer.load(str(p2), "dataset2")
    
    original_argv = sys.argv
    try:
        sys.argv = ["solution.py", "merge", "dataset1", "dataset2", "id", "merged_data"]
        sol.main()
        captured = capsys.readouterr()
        assert captured.out == "OK: dataset merged_data created with 2 rows\n"
    finally:
        sys.argv = original_argv

def test_load_duplicate_column_names(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "age", "name"], [["Alice", 25, "Alice2"], ["Bob", 30, "Bob2"]])
    
    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")
    
    assert result == "OK: dataset test_data loaded with 2 rows"
    df = analyzer.datasets["test_data"]
    assert len(df.columns) == 3
    assert "name" in df.columns
    assert "age" in df.columns
    expected_columns = ["name", "age", "name.1"]
    assert list(df.columns) == expected_columns

def test_load_mixed_type_data(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["id", "value"], [["1", "text"], ["2", 25.5], ["3", "more_text"]])
    
    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")
    
    assert result == "OK: dataset test_data loaded with 3 rows"
    df = analyzer.datasets["test_data"]
    assert df["value"].dtype == "object"

def test_date_formats(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "date1", "date2", "date3", "date4"], [
        ["Alice", "2023-01-01", "01/15/2023", "15-01-2023", "Jan 1, 2023"],
        ["Bob", "2023-02-01", "02/15/2023", "15-02-2023", "Feb 1, 2023"]
    ])
    
    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")
    
    assert result == "OK: dataset test_data loaded with 2 rows"
    df = analyzer.datasets["test_data"]
    assert df["date1"].dtype == "datetime64[ns]"
    assert df["date2"].dtype == "datetime64[ns]"
    assert df["date3"].dtype == "datetime64[ns]"
    assert df["date4"].dtype == "datetime64[ns]"

def test_merge_incompatible_column_types(tmp_path):
    p1 = tmp_path / "data1.csv"
    write_csv(p1, ["id", "value"], [["1", "text"], ["2", "more_text"]])
    
    p2 = tmp_path / "data2.csv"
    write_csv(p2, ["id", "value"], [["1", 25.5], ["2", 30.0]])
    
    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p1), "dataset1")
    analyzer.load(str(p2), "dataset2")
    
    result = analyzer.merge("dataset1", "dataset2", "value", "merged_data")
    assert result == "ERROR: operation failed"

def test_load_csv_extension_requirement(tmp_path):
    p = tmp_path / "data.txt"
    write_csv(p, ["name", "age", "score"], [["Alice", 25, 85.5], ["Bob", 30, 92.0]])
    
    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")
    
    assert result == "ERROR: invalid file format"


def test_type_inference_priority_numeric_over_date(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["year"], [["2022"], ["2023"], ["2024"]])

    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")

    assert result == "OK: dataset test_data loaded with 3 rows"
    df = analyzer.datasets["test_data"]
    assert pd.api.types.is_numeric_dtype(df["year"])


def test_numeric_median_fill_missing_values(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["value"], [[10], [20], [30], [""]])

    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")

    assert result == "OK: dataset test_data loaded with 4 rows"
    df = analyzer.datasets["test_data"]
    filled_values = df["value"].tolist()
    assert filled_values.count(20.0) >= 1
    assert not pd.isna(df["value"]).any()

def test_numeric_mode_fill_missing_values(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["value"], [[10], [20], [10], [20], [""]])

    analyzer = sol.DataAnalyzer()
    result = analyzer.load(str(p), "test_data")

    assert result == "OK: dataset test_data loaded with 5 rows"
    df = analyzer.datasets["test_data"]
    filled_values = df["value"].tolist()
    assert filled_values.count(10) >= 3
    assert not pd.isna(df["value"]).any()

def test_filter_date_invalid_value_format(tmp_path):
    p = tmp_path / "data.csv"
    write_csv(p, ["name", "date"], [["Alice", "2023-01-01"], ["Bob", "2023-01-02"]])

    analyzer = sol.DataAnalyzer()
    analyzer.load(str(p), "test_data")

    result = analyzer.filter("test_data", "date", ">", "not-a-date", "after_invalid")
    assert result == "ERROR: invalid value"
