
import os
import duckdb
from encoding_translator import (
    detect_encoding,
    get_duckdb_encoding,
    detect_delimiter,
    process_files,
    write_utf8_csv
)

# === Step 1: Define the path to your CSV directory ===
csv_directory = "/home/user/Documents/data/Carga_11-24"

# === Step 2: Create a DuckDB connection (in-memory or persistent) ===
con = duckdb.connect(database=":memory:")

# === Step 3: Process all CSV files in the directory ===
print("🔍 Scanning directory for CSV files...")
file_metadata = process_files(csv_directory)

# === Step 4: Load each file into DuckDB using detected metadata ===
for file in file_metadata:
    print(f"\n File: {file['filename']}")
    print(f" - Python encoding detected: {file['python_encoding']}")
    print(f" - DuckDB encoding mapped: {file['duckdb_encoding']} (via get_duckdb_encoding)")
    print(f" - Delimiter detected: '{file['delimiter']}'")
    print(f" - Target DuckDB table name: {file['table_name']}")

    # Load into DuckDB
    con.execute(f"""
        CREATE TABLE {file['table_name']} AS
        SELECT *
        FROM read_csv_auto(
            '{file["path"]}',
            delim='{file["delimiter"]}',
            encoding='{file["duckdb_encoding"]}'
        )
    """)

print("\n All files have been successfully loaded into DuckDB.")

# === Run a sample query on the first table ===
if file_metadata:
    sample_table = file_metadata[0]["table_name"]
    print(f"\n🔎 Sample query on '{sample_table}':")
    df = con.execute(f"SELECT * FROM {sample_table} LIMIT 5").fetchdf()
    print(df)

# === Demonstrate UTF-8 conversion ===
for file in file_metadata:
    utf8_path = os.path.join(csv_directory, f"utf8_{file['filename']}")
    write_utf8_csv(file["path"], utf8_path)
    print(f" - Converted '{file['filename']}' to UTF-8 → {utf8_path}")

# === Step 7: Demonstrate encoding detection ===
print("\n🧪 Encoding Detection Demo:")
sample_path = file_metadata[0]["path"] if file_metadata else None
if sample_path:
    encoding = detect_encoding(sample_path)
    print(f" - Encoding detected for '{os.path.basename(sample_path)}': {encoding}")

# === Step 8: Demonstrate DuckDB encoding translation ===

test_encodings = ["utf-8", "iso-8859-1", "windows-1252", "latin1", "ascii", "unknown-encoding"]
for enc in test_encodings:
    duckdb_enc = get_duckdb_encoding(enc)
    print(f" - Python encoding '{enc}' → DuckDB encoding '{duckdb_enc}'")

con.close()