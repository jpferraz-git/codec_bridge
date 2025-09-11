"""
example.py - Example usage of the EncodingDetector library

This script demonstrates how to:
1. Detect file encodings and delimiters from a folder of CSV files.
2. Map the detected Python encoding to DuckDB's expected encoding.
3. Load the files into DuckDB tables automatically.
"""

import duckdb
from .encoding_detector import EncodingDetector  # adjust the import to match your package structure

# Path to the directory containing CSV files
csv_directory_path = "/home/user/Documents/data/Carga_11-24"

# Create a DuckDB in-memory connection (you can use a file path for persistent storage)
connection = duckdb.connect(database=":memory:")

# Instantiate the encoding detector
detector = EncodingDetector(csv_directory_path)

# Process all CSV files and get metadata
file_results = detector.process_files()

# Iterate through detected files and create DuckDB tables
for result in file_results:
    print(f" Processing file: {result['filename']}")
    print(f" - Detected Python encoding: {result['python_encoding']}")
    print(f""" - Converted DuckDB encoding: {result['duckdb_encoding']}
          (via get_duckdb_encoding)""")
    print(f" - Detected delimiter: '{result['delimiter']}'")
    print(f" - Target table name: {result['table_name']}")

    # Create a DuckDB table using the detected properties
    connection.execute(f"""
        CREATE TABLE {result['table_name']} AS
        SELECT *
        FROM read_csv_auto(
            '{result["path"]}',
            delim='{result["delimiter"]}',
            encoding='{result["duckdb_encoding"]}'
        )
    """)

print("✅ All CSV files have been successfully loaded into DuckDB.")

# Example query on the first table
if file_results:
    table_name = file_results[0]["table_name"]
    print(f"\n🔎 Example query on table '{table_name}':")
    query_result = connection.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
    print(query_result)

# Close the connection
connection.close()
