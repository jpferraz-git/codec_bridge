# ENCODING-ICU-Library

# codec_bridge

A lightweight Python library that bridges encoding mismatches between Python and DuckDB when reading raw CSV files.

## 🚀 Motivation

DuckDB recently introduced the `encodings` extension, supporting over a thousand character encodings. However, when reading CSV files directly in Python, the encoding detected (e.g. `ISO-8859-1`) often uses a casing or format that DuckDB does not accept (e.g. `iso8859-1`).

This mismatch becomes a real problem in data pipelines that ingest large volumes of raw CSV files with diverse encodings. The goal of this library is to act as a **bridge**, translating Python-standard encoding names into DuckDB-compatible formats.

## 🔧 Features

- `get_duckdb_encoding`: Main method that maps Python encoding names to DuckDB-compatible ones.
- `detect_encoding`: Detects the encoding of a file using `charset-normalizer`.
- `detect_delimiter`: Identifies the most likely delimiter used in a CSV file.
- `write_utf8_csv`: Rewrites a file to UTF-8 encoding when necessary.
- `process_files`: Scans a directory of CSV files and returns metadata for each file.

## 📦 Installation

```bash
pip install codec_bridge
🧪 Example Usage
python
from codec_bridge import process_files, get_duckdb_encoding
import duckdb

# Path to your CSV directory
csv_dir = "/path/to/csvs"

# Create DuckDB connection
con = duckdb.connect(database=":memory:")

# Process files
files = process_files(csv_dir)

# Load into DuckDB
for f in files:
    con.execute(f"""
        CREATE TABLE {f['table_name']} AS
        SELECT * FROM read_csv_auto(
            '{f['path']}',
            delim='{f['delimiter']}',
            encoding='{f['duckdb_encoding']}'
        )
    """)
📚 Future Plans
Support for Spark and other engines facing similar encoding issues.

CLI tool for batch conversion and ingestion.

Integration with cloud storage (e.g. S3, GCS).

🧑‍💻 About
This library was created by a data engineering intern to solve real-world encoding issues in production pipelines. Contributions and feedback are welcome!
