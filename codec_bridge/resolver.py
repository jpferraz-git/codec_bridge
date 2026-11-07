import codecs
from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Literal
import weakref

import duckdb

from codec_bridge.repository.python_to_duckdb import PYTHON_TO_DUCKDB_ENCODING


class UnsupportedEncodingError(ValueError):
    """Raised when an encoding cannot be mapped to a DuckDB encoding name in strict mode."""


StrategyType = Literal["native", "extension", "static_map", "transcode"]

_NATIVE_ENCODINGS: dict[str, str] = {
    "utf-8": "utf-8",
    "ascii": "utf-8",
    "utf-16": "utf-16",
}

_PROBE_CACHE: weakref.WeakKeyDictionary[duckdb.DuckDBPyConnection, dict[str, bool]] = (
    weakref.WeakKeyDictionary()
)
_FALLBACK_PROBE_CACHE: dict[int, dict[str, bool]] = {}


@dataclass(frozen=True)
class EncodingResolution:
    """Immutable result of resolving a Python encoding name for DuckDB."""

    python_name: str
    duckdb_name: str | None
    strategy: StrategyType


def normalize_name(name: str | None) -> str:
    """
    Normalizes an encoding name to its canonical lowercase Python codec name.

    - None or empty/whitespace-only string becomes 'utf-8'.
    - 'utf-8-sig' (and aliases) becomes 'utf-8'.
    """
    if not name or not name.strip():
        return "utf-8"

    cleaned = name.strip().lower()
    try:
        canonical = codecs.lookup(cleaned).name.lower()
    except LookupError:
        canonical = cleaned

    if canonical in {"utf-8-sig", "utf_8_sig"}:
        return "utf-8"

    return canonical


def _has_c1_bytes_in_file(file_path: str | Path | None, chunk: int = 1000000) -> bool:
    """Check whether a file contains C1 control bytes (0x80..0x9F)."""
    if file_path is None:
        return False
    try:
        with open(file_path, "rb") as f:
            data = f.read(chunk)
        return any(0x80 <= b <= 0x9F for b in data)
    except OSError:
        return True


def _is_extension_loaded(con: duckdb.DuckDBPyConnection) -> bool:
    """Return True if the 'encodings' extension is loaded on the given connection."""
    try:
        row = con.execute(
            "SELECT loaded FROM duckdb_extensions() WHERE extension_name = 'encodings'"
        ).fetchone()
        return bool(row and row[0])
    except Exception:
        return False


def _ensure_extension(con: duckdb.DuckDBPyConnection, install_extension: bool) -> bool:
    """Ensure the 'encodings' extension is loaded on con, optionally installing it."""
    if _is_extension_loaded(con):
        return True
    try:
        if install_extension:
            con.execute("INSTALL encodings;")
        con.execute("LOAD encodings;")
        return _is_extension_loaded(con)
    except Exception:
        return False


def _in_duckdb_encodings_table(con: duckdb.DuckDBPyConnection, encoding_name: str) -> bool | None:
    """
    Check if encoding_name is listed in duckdb_encodings().
    Returns True/False if duckdb_encodings() exists, or None if the table function is unavailable.
    """
    try:
        row = con.execute(
            "SELECT 1 FROM duckdb_encodings() WHERE lower(name) = lower(?) LIMIT 1",
            [encoding_name],
        ).fetchone()
        return row is not None
    except duckdb.Error:
        return None


def _get_conn_cache(con: duckdb.DuckDBPyConnection) -> dict[str, bool]:
    try:
        return _PROBE_CACHE.setdefault(con, {})
    except TypeError:
        return _FALLBACK_PROBE_CACHE.setdefault(id(con), {})


def probe_encoding(con: duckdb.DuckDBPyConnection, encoding_name: str) -> bool:
    """
    Probe whether DuckDB's read_csv accepts encoding_name on the given connection.
    Creates a one-line temporary CSV, executes read_csv, catches InvalidInputException,
    and caches the boolean result per connection and encoding name.
    """
    key = encoding_name.lower()
    cache = _get_conn_cache(con)
    if key in cache:
        return cache[key]

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=True) as tmp:
        tmp.write(b"a,b\n1,2\n")
        tmp.flush()
        try:
            con.execute(
                "SELECT * FROM read_csv(?, encoding=?)",
                [tmp.name, encoding_name],
            ).fetchall()
            accepted = True
        except duckdb.InvalidInputException:
            accepted = False
        except duckdb.Error:
            accepted = False

    cache[key] = accepted
    return accepted


def resolve_encoding(
    name: str | None,
    con: duckdb.DuckDBPyConnection | None = None,
    install_extension: bool = False,
    *,
    file_path: str | Path | None = None,
    has_c1_bytes: bool | None = None,
) -> EncodingResolution:
    """
    Resolve a Python encoding name into a DuckDB-compatible encoding strategy.

    Order of resolution:
    (a) Native core encodings ('utf-8', 'utf-16'; native 'latin-1' only when the file
        is confirmed to have no bytes in 0x80..0x9F).
    (b) With the 'encodings' extension loaded on `con`, accept the name directly if it
        is present in `duckdb_encodings()` or passes a `read_csv` probe.
    (c) Validated static fallback map (`PYTHON_TO_DUCKDB_ENCODING`). If `con` is provided
        with the extension loaded, the mapped target is also verified via probe.
    (d) Fallback to `transcode` (`duckdb_name=None`).
    """
    norm = normalize_name(name)

    # (a) Native core encodings
    if norm in _NATIVE_ENCODINGS:
        return EncodingResolution(
            python_name=norm,
            duckdb_name=_NATIVE_ENCODINGS[norm],
            strategy="native",
        )

    if norm == "iso8859-1":
        c1 = has_c1_bytes
        if c1 is None and file_path is not None:
            c1 = _has_c1_bytes_in_file(file_path)
        if c1 is False:
            return EncodingResolution(
                python_name=norm,
                duckdb_name="latin-1",
                strategy="native",
            )

    # (b) Runtime resolution against connection with extension loaded
    ext_loaded = False
    if con is not None:
        ext_loaded = _ensure_extension(con, install_extension=install_extension)
        if ext_loaded:
            candidates = [norm]
            raw_clean = (name or "").strip().lower()
            if raw_clean and raw_clean not in candidates:
                candidates.append(raw_clean)

            for candidate in candidates:
                in_table = _in_duckdb_encodings_table(con, candidate)
                if in_table is True or probe_encoding(con, candidate):
                    return EncodingResolution(
                        python_name=norm,
                        duckdb_name=candidate,
                        strategy="extension",
                    )

    # (c) Validated static fallback map
    mapped = PYTHON_TO_DUCKDB_ENCODING.get(norm)
    if mapped is not None:
        if con is None or not ext_loaded or probe_encoding(con, mapped):
            return EncodingResolution(
                python_name=norm,
                duckdb_name=mapped,
                strategy="static_map",
            )

    # (d) Transcode fallback
    return EncodingResolution(
        python_name=norm,
        duckdb_name=None,
        strategy="transcode",
    )
