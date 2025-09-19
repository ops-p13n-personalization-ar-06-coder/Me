import sys
import pandas as pd
import numpy as np

class DataAnalyzer:
    def __init__(self):
        self.datasets = {}
    
    def load(self, csv_file, dataset_name):
        # TODO: Load CSV file and store with dataset_name
        # Handle missing values by filling with median for numeric, mode for text
        # Type inference: numeric > date > text
        # Save to datasets/<dataset_name>.pkl
        # Return "OK: dataset <name> loaded with <rows> rows" or error message
        pass
    
    def describe(self, dataset_name):
        # TODO: Show statistical summary of the dataset
        # Return formatted string with dataset info and column statistics
        pass
    
    def compare(self, dataset1, dataset2, column_name):
        # TODO: Compare a specific column between two datasets
        # Return formatted comparison string or error message
        pass
    
    def export(self, dataset_name, output_file):
        # TODO: Export dataset to Excel format
        # Return "OK: dataset <name> exported to <output_file>" or error message
        pass
    
    def filter(self, dataset_name, column_name, operator, value, new_dataset_name):
        # TODO: Filter dataset based on column condition and save as new dataset
        # Supported operators: ">", "<", ">=", "<=", "==", "!=", "contains", "not_contains"
        # Return "OK: dataset <new_name> created with <rows> rows" or error message
        pass
    
    def merge(self, dataset1, dataset2, column_name, new_dataset_name):
        # TODO: Merge two datasets on a common column and save as new dataset
        # Return "OK: dataset <new_name> created with <rows> rows" or error message
        pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python solution.py <command> [args]")
        return
    
    analyzer = DataAnalyzer()
    command = sys.argv[1]
    
    if command == "load":
        if len(sys.argv) != 4:
            print("Usage: python solution.py load <csv_file> <dataset_name>")
            return
        result = analyzer.load(sys.argv[2], sys.argv[3])
        print(result)
    
    elif command == "describe":
        if len(sys.argv) != 3:
            print("Usage: python solution.py describe <dataset_name>")
            return
        result = analyzer.describe(sys.argv[2])
        print(result)
    
    elif command == "compare":
        if len(sys.argv) != 5:
            print("Usage: python solution.py compare <dataset1> <dataset2> <column_name>")
            return
        result = analyzer.compare(sys.argv[2], sys.argv[3], sys.argv[4])
        print(result)
    
    elif command == "export":
        if len(sys.argv) != 4:
            print("Usage: python solution.py export <dataset_name> <output_file>")
            return
        result = analyzer.export(sys.argv[2], sys.argv[3])
        print(result)
    
    elif command == "filter":
        if len(sys.argv) != 7:
            print("Usage: python solution.py filter <dataset_name> <column_name> <operator> <value> <new_dataset_name>")
            return
        result = analyzer.filter(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print(result)
    
    elif command == "merge":
        if len(sys.argv) != 6:
            print("Usage: python solution.py merge <dataset1> <dataset2> <column_name> <new_dataset_name>")
            return
        result = analyzer.merge(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        print(result)
    
    else:
        print("Unknown command:", command)

if __name__ == "__main__":
    main()
