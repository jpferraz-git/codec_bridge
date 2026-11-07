# Upstream DuckDB Encoding Support Check

This document records the runtime verification of DuckDB core and the `encodings` extension across the minimum supported version (`duckdb==1.3.2`) and the latest release (`duckdb==2.0.0`).

- **Date of execution:** 2026-11-06
- **Python version:** 3.12.3

## Summary of Findings

1. **`duckdb==2.0.0`** (extension version `2d1447a890`):
   - `INSTALL encodings; LOAD encodings;` succeeds.
   - `SELECT count(*) FROM duckdb_encodings();` returns **1351** registered encoding names/aliases.
   - Accepts common Python/IANA aliases directly (`windows-1252`, `ISO-8859-1`, `latin1`, `cp1252`).
   - Rejects `utf8` (without hyphen) and `utf-16le` (endianness-specific UTF-16 without BOM).

2. **`duckdb==1.3.2`** (extension version `dc3c206`):
   - `INSTALL encodings; LOAD encodings;` succeeds.
   - `duckdb_encodings()` **does not exist**: raises `CatalogException: Catalog Error: Table Function with name duckdb_encodings does not exist!`.
   - Rejects hyphenated/Python alias forms such as `windows-1252`, `ISO-8859-1`, `latin1`, `utf8`, and `utf-16le`, while accepting `cp1252` (and underscore variants from the legacy registration table).

## Verification Matrix

| DuckDB Version | Extension Version | `duckdb_encodings()` | Encoding Tested | Result | Error Message |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `2.0.0` | `2d1447a890` | `1351` rows | `windows-1252` | Accepted | — |
| `2.0.0` | `2d1447a890` | `1351` rows | `ISO-8859-1` | Accepted | — |
| `2.0.0` | `2d1447a890` | `1351` rows | `latin1` | Accepted | — |
| `2.0.0` | `2d1447a890` | `1351` rows | `utf8` | Rejected | `InvalidInputException: Invalid Input Error: The CSV Reader does not support the encoding: "utf8"` |
| `2.0.0` | `2d1447a890` | `1351` rows | `utf-16le` | Rejected | `InvalidInputException: Invalid Input Error: The CSV Reader does not support the encoding: "utf-16le"` |
| `2.0.0` | `2d1447a890` | `1351` rows | `cp1252` | Accepted | — |
| `1.3.2` | `dc3c206` | Missing (`CatalogException`) | `windows-1252` | Rejected | `InvalidInputException: Invalid Input Error: The CSV Reader does not support the encoding: "windows-1252"` |
| `1.3.2` | `dc3c206` | Missing (`CatalogException`) | `ISO-8859-1` | Rejected | `InvalidInputException: Invalid Input Error: The CSV Reader does not support the encoding: "ISO-8859-1"` |
| `1.3.2` | `dc3c206` | Missing (`CatalogException`) | `latin1` | Rejected | `InvalidInputException: Invalid Input Error: The CSV Reader does not support the encoding: "latin1"` |
| `1.3.2` | `dc3c206` | Missing (`CatalogException`) | `utf8` | Rejected | `InvalidInputException: Invalid Input Error: The CSV Reader does not support the encoding: "utf8"` |
| `1.3.2` | `dc3c206` | Missing (`CatalogException`) | `utf-16le` | Rejected | `InvalidInputException: Invalid Input Error: The CSV Reader does not support the encoding: "utf-16le"` |
| `1.3.2` | `dc3c206` | Missing (`CatalogException`) | `cp1252` | Accepted | — |

## Design Implications for Phase 3 (`codec_bridge/resolver.py`)

- **Normalization is required before resolution:** Because `utf8` is rejected even in DuckDB 2.0.0 while core natively accepts `utf-8`, `normalize_name` must canonicalize `utf8` / `utf_8` / `utf-8-sig` to `utf-8` first.
- **`duckdb_encodings()` is optional at runtime:** Since DuckDB 1.3.2 does not provide `duckdb_encodings()`, the resolver must catch `duckdb.CatalogException` (or generic `duckdb.Error`) when querying `duckdb_encodings()` and fall back transparently to a runtime `read_csv` probe.
- **Legacy static map remains necessary for DuckDB 1.3.2:** In DuckDB 1.3.2, names like `iso-8859-1` / `latin1` are rejected directly by the extension, requiring the validated static fallback table (e.g., mapping `iso8859-1` -> `latin_1`, `cp1252` -> `windows_1252`) when direct probing of the normalized Python name fails.
- **Endianness-specific BOM-less UTF-16 (`utf-16-le`, `utf-16-be`) requires transcoding:** Both DuckDB 1.3.2 and 2.0.0 reject `utf-16le` (and `utf-16-le` / `utf-16-be`), so BOM-less UTF-16LE/BE or UTF-32 must resolve to the `transcode` strategy.
