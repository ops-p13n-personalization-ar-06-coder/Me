import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import pickle

class DataAnalyzer:
    def __init__(self):
        self.datasets = {}
        # BUG: not creating datasets dir reliably (missing exist_ok=True)
        self.datasets_dir = Path("datasets")
        try:
            os.mkdir(self.datasets_dir)
        except Exception:
            pass
    
    def _get_dataset(self, name):
        if name in self.datasets:
            return self.datasets[name]
        p = self.datasets_dir / f"{name}.pkl"
        # BUG: does not load from pickle on demand
        if not p.exists():
            return None
        try:
            with open(p, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None

    def load(self, csv_file, dataset_name):
        # BUG: does not check file existence first
        if not str(csv_file).endswith(".csv"):
            return "ERROR: invalid file format"
        try:
            df = pd.read_csv(csv_file)  # may raise
        except Exception:
            return "ERROR: invalid file format"
        if df.shape[0] == 0:
            return "ERROR: invalid file format"
        # BUG: header validation missing; numeric-only first row should be invalid
        
        # BUG: no date detection; no type inference priority
        # BUG: does not treat empty strings as missing for text columns
        # BUG: missing filling policy incorrect
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # wrong policy: fill with mean always
                df[col] = df[col].fillna(df[col].mean())
            else:
                # wrong: leave empty strings as is
                df[col] = df[col].fillna(method="ffill")
        
        # BUG: does not persist correctly if dir is missing
        self.datasets[dataset_name] = df
        try:
            with open(self.datasets_dir / f"{dataset_name}.pkl", "wb") as f:
                pickle.dump(df, f)
        except Exception:
            pass
        return f"OK: dataset {dataset_name} loaded with {len(df)} rows"
    
    def describe(self, dataset_name):
        df = self._get_dataset(dataset_name)
        if df is None:
            return "ERROR: dataset not found"
        # BUG: wrong formatting and rounding
        lines = [f"Dataset: {dataset_name}", f"Shape: {df.shape[0]} rows, {df.shape[1]} columns", "Columns:"]
        for c in df.columns:
            s = df[c].describe(include='all')
            lines.append(f"- {c}: {df[c].dtype} ({', '.join([f'{k}={v}' for k, v in s.items() if k in ['count','mean','std','min','25%','50%','75%','max','unique','top','freq']])})")
        return "\n".join(lines)
    
    def compare(self, dataset1, dataset2, column_name):
        df1 = self._get_dataset(dataset1)
        df2 = self._get_dataset(dataset2)
        if df1 is None or df2 is None:
            return "ERROR: dataset not found"
        if column_name not in df1.columns or column_name not in df2.columns:
            return "ERROR: column not found"
        s1, s2 = df1[column_name], df2[column_name]
        # BUG: allow non-numeric; and difference sign reversed
        m1, sd1, n1 = s1.mean(), s1.std(), s1.count()
        m2, sd2, n2 = s2.mean(), s2.std(), s2.count()
        diff = m2 - m1
        return f"Comparison: {column_name} between {dataset1} and {dataset2}\n{dataset1}: mean={m1:.2f} std={sd1:.2f} count={n1}\n{dataset2}: mean={m2:.2f} std={sd2:.2f} count={n2}\nDifference: {diff:.2f}"
    
    def export(self, dataset_name, output_file):
        df = self._get_dataset(dataset_name)
        if df is None:
            return "ERROR: dataset not found"
        try:
            # BUG: write CSV, not Excel; and still claim OK
            df.to_csv(output_file, index=False)
            return f"OK: dataset {dataset_name} exported to {output_file}"
        except Exception:
            return "ERROR: invalid file format"
    
    def filter(self, dataset_name, column_name, operator, value, new_dataset_name):
        df = self._get_dataset(dataset_name)
        if df is None:
            return "ERROR: dataset not found"
        if column_name not in df.columns:
            return "ERROR: column not found"
        s = df[column_name]
        try:
            if operator == ">":
                mask = s > float(value)
            elif operator == "<":
                mask = s < float(value)
            elif operator == ">=":
                mask = s >= float(value)
            elif operator == "<=":
                mask = s <= float(value)
            elif operator == "==":
                mask = s == value  # BUG: comparing string to numeric without cast
            elif operator == "!=":
                mask = s != value
            elif operator == "contains":
                # BUG: only case-sensitive contains and allowed on any dtype
                mask = s.astype(str).str.contains(str(value))
            elif operator == "not_contains":
                mask = ~s.astype(str).str.contains(str(value))
            else:
                return "ERROR: invalid operator"
        except Exception:
            return "ERROR: invalid value"
        out = df[mask]
        if out.empty:
            return "ERROR: operation failed"
        self.datasets[new_dataset_name] = out
        try:
            with open(self.datasets_dir / f"{new_dataset_name}.pkl", "wb") as f:
                pickle.dump(out, f)
        except Exception:
            pass
        return f"OK: dataset {new_dataset_name} created with {len(out)} rows"
    
    def merge(self, dataset1, dataset2, column_name, new_dataset_name):
        df1 = self._get_dataset(dataset1)
        df2 = self._get_dataset(dataset2)
        if df1 is None or df2 is None:
            return "ERROR: dataset not found"
        if column_name not in df1.columns or column_name not in df2.columns:
            return "ERROR: column not found"
        try:
            # BUG: use outer merge, not inner; no type compatibility check; no suffix handling
            merged = df1.merge(df2, on=column_name, how="outer")
            if merged.empty:
                return "ERROR: operation failed"
            self.datasets[new_dataset_name] = merged
            with open(self.datasets_dir / f"{new_dataset_name}.pkl", "wb") as f:
                pickle.dump(merged, f)
            return f"OK: dataset {new_dataset_name} created with {len(merged)} rows"
        except Exception:
            return "ERROR: operation failed"


def main():
    if len(sys.argv) < 2:
        print("Usage: python solution.py <command> [args]")
        return
    analyzer = DataAnalyzer()
    cmd = sys.argv[1]
    if cmd == "load" and len(sys.argv) == 4:
        print(analyzer.load(sys.argv[2], sys.argv[3]))
    elif cmd == "describe" and len(sys.argv) == 3:
        print(analyzer.describe(sys.argv[2]))
    elif cmd == "compare" and len(sys.argv) == 5:
        print(analyzer.compare(sys.argv[2], sys.argv[3], sys.argv[4]))
    elif cmd == "export" and len(sys.argv) == 4:
        print(analyzer.export(sys.argv[2], sys.argv[3]))
    elif cmd == "filter" and len(sys.argv) == 7:
        print(analyzer.filter(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))
    elif cmd == "merge" and len(sys.argv) == 6:
        print(analyzer.merge(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
    else:
        print("Unknown or invalid usage")

if __name__ == "__main__":
    main()
