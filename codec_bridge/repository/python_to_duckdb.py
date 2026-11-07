"""
Minimal legacy fallback mapping from normalized Python codec names to DuckDB encoding names.

Note:
    Recent versions of DuckDB's `encodings` extension natively accept standard Python
    and IANA encoding aliases (such as `windows-1252`, `iso-8859-1`, `latin1`, `koi8-r`,
    `cp932`). This static table serves as a validated fallback for older DuckDB releases
    (e.g., DuckDB 1.3.2) where the `encodings` extension lacks Python alias registration
    or when resolving encodings without an active DuckDB connection.

    Every key in `PYTHON_TO_DUCKDB_ENCODING` MUST be normalized via `normalize_name(key)`,
    and every target value MUST be accepted by DuckDB with the `encodings` extension loaded.
"""

PYTHON_TO_DUCKDB_ENCODING: dict[str, str] = {
    # --- Core / Unicode ---
    "utf-8": "utf-8",
    "ascii": "utf-8",
    "utf-16": "utf-16",
    # --- ISO-8859 family ---
    "iso8859-1": "ISO_8859_1",
    "iso8859-2": "ISO_8859_2",
    "iso8859-5": "ISO_8859_5",
    "iso8859-7": "ISO_8859_7",
    "iso8859-10": "ISO_8859_10",
    "iso8859-14": "ISO_8859_14",
    "iso8859-15": "ISO_8859_15",
    # --- Windows / DOS code pages ---
    "cp1250": "cp1250",
    "cp1251": "cp1251",
    "cp1252": "cp1252",
    "cp1253": "cp1253",
    "cp1254": "cp1254",
    "cp1255": "cp1255",
    "cp1256": "cp1256",
    "cp1257": "cp1257",
    "cp1258": "cp1258",
    "cp852": "cp852",
    # --- Cyrillic & Mac ---
    "koi8-r": "koi8_r",
    "koi8-u": "koi8_u",
    "mac-iceland": "MAC_IS",
    # --- East Asian ---
    "shift_jis": "shift_jis",
    "cp932": "shift_jis",
    "euc_jp": "euc_jp",
    "gbk": "gb18030",
    "gb2312": "gb18030",
    "gb18030": "gb18030",
    "big5": "big5",
    "euc_kr": "euc_kr",
    "cp949": "cp949",
}
