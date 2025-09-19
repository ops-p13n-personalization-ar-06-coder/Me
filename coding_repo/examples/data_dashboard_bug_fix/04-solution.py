import sys
import pandas as pd
import numpy as np
import os
import pickle
from pathlib import Path
from datetime import datetime
import re

class DataAnalyzer:
    def __init__(self):
        self.datasets = {}
        self.datasets_dir = Path("datasets")
        self.datasets_dir.mkdir(exist_ok=True)
    
    def load(self, csv_file, dataset_name):
        if not os.path.exists(csv_file):
            return "ERROR: file not found"
        
        if not csv_file.endswith('.csv'):
            return "ERROR: invalid file format"
        
        try:
            df = pd.read_csv(csv_file)
        except Exception:
            return "ERROR: invalid file format"
        
        if df.empty:
            return "ERROR: invalid file format"
        
        try:
            numeric_cols = sum(1 for col in df.columns if str(col).replace('.', '').replace('-', '').isdigit())
            if numeric_cols == len(df.columns) and len(df.columns) > 0:
                return "ERROR: invalid file format"
        except:
            pass
        
        df = self._detect_date_columns(df)
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
            
                value_counts = df[col].value_counts(dropna=True)
                if not value_counts.empty and value_counts.max() >= 2:
                    modes = value_counts[value_counts == value_counts.max()].index.tolist()
                    
                    mode_value = float(min(modes))
                    df[col] = df[col].fillna(mode_value)
                else:
                    df[col] = df[col].fillna(df[col].median())
            elif df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].replace('', pd.NA)
                df[col] = df[col].fillna(self._get_mode(df[col]))
        
        self.datasets[dataset_name] = df
        pickle_path = self.datasets_dir / f"{dataset_name}.pkl"
        with open(pickle_path, 'wb') as f:
            pickle.dump(df, f)
        return f"OK: dataset {dataset_name} loaded with {len(df)} rows"
    
    def _get_dataset(self, dataset_name):
        if dataset_name in self.datasets:
            return self.datasets[dataset_name]
        
        pickle_path = self.datasets_dir / f"{dataset_name}.pkl"
        if pickle_path.exists():
            with open(pickle_path, 'rb') as f:
                df = pickle.load(f)
            self.datasets[dataset_name] = df
            return df
        
        return None
    
    def _get_mode(self, series):
        if series.empty:
            return 'N/A'
        value_counts = series.value_counts()
        max_freq = value_counts.max()
        modes = value_counts[value_counts == max_freq].index
        if len(modes) == 1:
            return modes[0]
        else:
            return sorted(modes)[0]
    
    def _detect_date_columns(self, df):
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(10)
                if len(sample) > 0:
                    try:
                        pd.to_numeric(sample, errors='raise')
                        continue
                    except:
                        pass
                    
                    try:
                        converted = pd.to_datetime(sample, errors='coerce')
                        if not converted.isna().all():
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                    except:
                        pass
        return df
    
    def _validate_data_types(self, df, column_name, expected_type):
        if column_name not in df.columns:
            return False, "ERROR: column not found"
        
        col = df[column_name]
        
        if expected_type == 'numeric':
            if col.dtype not in ['int64', 'float64']:
                return False, "ERROR: column not found"
        elif expected_type == 'text':
            if col.dtype not in ['object']:
                return False, "ERROR: column not found"
        elif expected_type == 'date':
            if col.dtype != 'datetime64[ns]':
                return False, "ERROR: column not found"
        
        return True, None
    
    def _parse_filter_value(self, value, column_dtype):
        try:
            if column_dtype in ['int64', 'float64']:
                return float(value)
            elif column_dtype == 'datetime64[ns]':
                # Enforce strict YYYY-MM-DD format
                return pd.to_datetime(value, format="%Y-%m-%d", errors='raise')
            else:
                return str(value)
        except:
            return None
    
    def filter(self, dataset_name, column_name, operator, value, new_dataset_name):
        df = self._get_dataset(dataset_name)
        if df is None:
            return "ERROR: dataset not found"
        
        if column_name not in df.columns:
            return "ERROR: column not found"
        
        valid_operators = ['==', '!=', '<', '>', '<=', '>=', 'contains', 'not_contains']
        if operator not in valid_operators:
            return "ERROR: invalid operator"
        
        col = df[column_name]
        
        parsed_value = self._parse_filter_value(value, col.dtype)
        if parsed_value is None:
            return "ERROR: invalid value"
        
        try:
            if operator == '==':
                filtered_df = df[col == parsed_value]
            elif operator == '!=':
                filtered_df = df[col != parsed_value]
            elif operator == '<':
                filtered_df = df[col < parsed_value]
            elif operator == '>':
                filtered_df = df[col > parsed_value]
            elif operator == '<=':
                filtered_df = df[col <= parsed_value]
            elif operator == '>=':
                filtered_df = df[col >= parsed_value]
            elif operator == 'contains':
                if col.dtype != 'object':
                    return "ERROR: invalid operator"
                filtered_df = df[col.astype(str).str.contains(str(parsed_value), case=False, na=False)]
            elif operator == 'not_contains':
                if col.dtype != 'object':
                    return "ERROR: invalid operator"
                filtered_df = df[~col.astype(str).str.contains(str(parsed_value), case=False, na=False)]
            
            if len(filtered_df) == 0:
                return "ERROR: operation failed"
            
            self.datasets[new_dataset_name] = filtered_df
            
            pickle_path = self.datasets_dir / f"{new_dataset_name}.pkl"
            with open(pickle_path, 'wb') as f:
                pickle.dump(filtered_df, f)
            
            return f"OK: dataset {new_dataset_name} created with {len(filtered_df)} rows"
            
        except Exception:
            return "ERROR: operation failed"
    
    def merge(self, dataset1, dataset2, on_column, new_dataset_name):
        df1 = self._get_dataset(dataset1)
        if df1 is None:
            return "ERROR: dataset not found"
        
        df2 = self._get_dataset(dataset2)
        if df2 is None:
            return "ERROR: dataset not found"
        
        if on_column not in df1.columns:
            return "ERROR: column not found"
        if on_column not in df2.columns:
            return "ERROR: column not found"
        
        col1_type = df1[on_column].dtype
        col2_type = df2[on_column].dtype
        
        if col1_type in ['int64', 'float64'] and col2_type not in ['int64', 'float64']:
            return "ERROR: operation failed"
        if col1_type not in ['int64', 'float64'] and col2_type in ['int64', 'float64']:
            return "ERROR: operation failed"
        
        try:
            df1_suffix = df1.copy()
            df2_suffix = df2.copy()
            
            common_cols = set(df1.columns) & set(df2.columns) - {on_column}
            
            for col in common_cols:
                if col in df1_suffix.columns:
                    df1_suffix = df1_suffix.rename(columns={col: f"{col}_x"})
                if col in df2_suffix.columns:
                    df2_suffix = df2_suffix.rename(columns={col: f"{col}_y"})
            
            merged_df = pd.merge(df1_suffix, df2_suffix, on=on_column, how='inner')
            
            if len(merged_df) == 0:
                return "ERROR: operation failed"
            
            self.datasets[new_dataset_name] = merged_df
            
            pickle_path = self.datasets_dir / f"{new_dataset_name}.pkl"
            with open(pickle_path, 'wb') as f:
                pickle.dump(merged_df, f)
            
            return f"OK: dataset {new_dataset_name} created with {len(merged_df)} rows"
            
        except Exception:
            return "ERROR: operation failed"
    
    def describe(self, dataset_name):
        df = self._get_dataset(dataset_name)
        if df is None:
            return "ERROR: dataset not found"
        result = f"Dataset: {dataset_name}\n"
        result += f"Shape: {len(df)} rows, {len(df.columns)} columns\n"
        result += "Columns:\n"
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats = df[col].describe()
                result += f"- {col}: {df[col].dtype} (count={int(stats['count'])}, mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, 25%={stats['25%']:.2f}, 50%={stats['50%']:.2f}, 75%={stats['75%']:.2f}, max={stats['max']:.2f})\n"
            elif df[col].dtype == 'datetime64[ns]':
                count = df[col].count()
                unique = df[col].nunique()
                top = self._get_mode(df[col])
                freq = df[col].value_counts().iloc[0] if not df[col].empty else 0
                result += f"- {col}: {df[col].dtype} (count={count}, unique={unique}, top={top}, freq={freq})\n"
            else:
                count = df[col].count()
                unique = df[col].nunique()
                top = self._get_mode(df[col])
                freq = df[col].value_counts().iloc[0] if not df[col].empty else 0
                result += f"- {col}: {df[col].dtype} (count={count}, unique={unique}, top={top}, freq={freq})\n"
        
        return result.rstrip()
    
    def compare(self, dataset1, dataset2, column_name):
        df1 = self._get_dataset(dataset1)
        if df1 is None:
            return "ERROR: dataset not found"
        
        df2 = self._get_dataset(dataset2)
        if df2 is None:
            return "ERROR: dataset not found"
        
        if column_name not in df1.columns:
            return "ERROR: column not found"
        if column_name not in df2.columns:
            return "ERROR: column not found"
        
        col1 = df1[column_name]
        col2 = df2[column_name]
        
        if col1.dtype in ['int64', 'float64'] and col2.dtype in ['int64', 'float64']:
            mean1 = col1.mean()
            std1 = col1.std()
            count1 = col1.count()
            mean2 = col2.mean()
            std2 = col2.std()
            count2 = col2.count()
            diff = mean1 - mean2
            
            result = f"Comparison: {column_name} between {dataset1} and {dataset2}\n"
            result += f"{dataset1}: mean={mean1:.2f} std={std1:.2f} count={count1}\n"
            result += f"{dataset2}: mean={mean2:.2f} std={std2:.2f} count={count2}\n"
            result += f"Difference: {diff:.2f}"
            
            return result
        else:
            return "ERROR: column not found"
    
    def export(self, dataset_name, output_file):
        df = self._get_dataset(dataset_name)
        if df is None:
            return "ERROR: dataset not found"
        
        try:
            df.to_excel(output_file, index=False)
            return f"OK: dataset {dataset_name} exported to {output_file}"
        except Exception:
            return "ERROR: invalid file format"

_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = DataAnalyzer()
    return _analyzer

def main():
    if len(sys.argv) < 2:
        print("Usage: python solution.py <command> [args]")
        return
    
    command = sys.argv[1]
    
    if command == "load":
        if len(sys.argv) != 4:
            print("Usage: python solution.py load <csv_file> <dataset_name>")
            return
        result = get_analyzer().load(sys.argv[2], sys.argv[3])
        print(result)
    
    elif command == "describe":
        if len(sys.argv) != 3:
            print("Usage: python solution.py describe <dataset_name>")
            return
        result = get_analyzer().describe(sys.argv[2])
        print(result)
    
    elif command == "compare":
        if len(sys.argv) != 5:
            print("Usage: python solution.py compare <dataset1> <dataset2> <column_name>")
            return
        result = get_analyzer().compare(sys.argv[2], sys.argv[3], sys.argv[4])
        print(result)
    
    elif command == "export":
        if len(sys.argv) != 4:
            print("Usage: python solution.py export <dataset_name> <output_file>")
            return
        result = get_analyzer().export(sys.argv[2], sys.argv[3])
        print(result)
    
    elif command == "filter":
        if len(sys.argv) != 7:
            print("Usage: python solution.py filter <dataset_name> <column_name> <operator> <value> <new_dataset_name>")
            return
        result = get_analyzer().filter(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print(result)
    
    elif command == "merge":
        if len(sys.argv) != 6:
            print("Usage: python solution.py merge <dataset1> <dataset2> <column_name> <new_dataset_name>")
            return
        result = get_analyzer().merge(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        print(result)
    
    else:
        print("Unknown command:", command)

if __name__ == "__main__":
    main()
