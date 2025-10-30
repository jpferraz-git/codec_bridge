"""
example.py — How to use codec_bridge

This script demonstrates how to:
1. Detect the encoding of CSV files using Python.
2. Translate the detected encoding to the correct format expected by DuckDB.
3. Automatically load CSV files into DuckDB using the translated encoding.
"""

import duckdb
from src.codec_bridge.encoding_translator import process_files, get_duckdb_encoding

# Path to the directory containing CSV files
csv_directory = "/path/to/your/csvs"

# Create a DuckDB connectio
con = duckdb.connect(database=":memory:")

# Process all CSV files and extract metadata
files = process_files(csv_directory)

# For each file, use get_duckdb_encoding to fix encoding mismatch
for file in files:
    print(f"\n File: {file['filename']}")
    print(f" - Python detected encoding: {file['python_encoding']}")

    # Core logic: translate encoding using the main method
    duckdb_encoding = get_duckdb_encoding(file['python_encoding'])
    print(f" - DuckDB-compatible encoding: {duckdb_encoding}")

    print(f" - Detected delimiter: '{file['delimiter']}'")
    print(f" - Target table name: {file['table_name']}")

    # Load the file into DuckDB using the translated encoding
    con.execute(f"""
        CREATE TEMP TABLE {file['table_name']} AS
        SELECT *
        FROM read_csv_auto(
            '{file["path"]}',
            delim='{file["delimiter"]}',
            encoding='{duckdb_encoding}'
        )
    """)

print("\n All files successfully loaded into DuckDB.")

con.close()