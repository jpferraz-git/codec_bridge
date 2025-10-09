# codec_bridge

A Python utility library that bridges encoding mismatches between Python and DuckDB when reading raw CSV files.

## 🔍 Motivation

DuckDB recently introduced the `encodings` extension, supporting over a thousand character encodings. However, Python often detects encodings using a format or casing that DuckDB does not accept directly. 

For example:
- Python detects: `ISO-8859-1`
- DuckDB expects: `latin`

This mismatch can break ingestion pipelines, especially when dealing with large volumes of raw CSV files from diverse sources. The goal of this library is to act as a **bridge**, translating Python-standard encoding names into DuckDB-compatible formats.

## ⚙️ Features

- ✅ `get_duckdb_encoding`: Main method that maps Python encoding names to DuckDB-compatible formats.
- 🔍 `detect_encoding`: Detects the encoding of a file using `charset-normalizer`.
- 📌 `detect_delimiter`: Identifies the most likely delimiter used in a CSV file.
- ✍️ `write_utf8_csv`: Rewrites a file to UTF-8 encoding when necessary.
- 📦 `process_files`: Scans a directory of CSV files and returns metadata for each file.

## 📦 Installation

```bash
pip install codec_bridge
```

## 🔧 Requirements

This library depends on:

- `duckdb` (>=1.3.2)
- `charset-normalizer` (>=3.4.2)

These will be installed automatically when using `pip install codec_bridge`.
