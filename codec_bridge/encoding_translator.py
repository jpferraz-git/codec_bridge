import csv
from pathlib import Path
import charset_normalizer
import os
import re
import logging

from codec_bridge.repository.python_to_duckdb import PYTHON_TO_DUCKDB_ENCODING

logger = logging.getLogger(__name__)


class EncodingDetectionError(Exception):
    """Raised when character encoding detection fails and strict mode is enabled."""

def get_duckdb_encoding(python_encoding_name: str) -> str:
    """
    Translates a Python-standard encoding name to the name expected by DuckDB.
    If no specific mapping is found, it returns the original name as a fallback.

    :param python_encoding_name: The encoding name detected (e.g., 'iso-8859-1').
    :return: The translated encoding name for DuckDB (e.g., 'ibm-819').
    """
    if not python_encoding_name:
        return "utf-8"

    normalized = python_encoding_name.lower()

    duckdb_encoding = PYTHON_TO_DUCKDB_ENCODING.get(normalized)

    if duckdb_encoding is None:
        logger.warning(
            f"Encoding {python_encoding_name} not mapped yet, falling back to utf-8"
        )
        return "utf-8"

    return duckdb_encoding


def _has_c1_control_bytes(data: bytes) -> bool:
    """Return True if data contains bytes in the 0x80-0x9F range."""
    return any(0x80 <= b <= 0x9F for b in data)


def detect_encoding(
    file_path: str | os.PathLike,
    chunk: int = 1000000,
    strict: bool = False,
) -> str:
    """
    Detects the character encoding of a file using BOM inspection and charset_normalizer.

    :param file_path: The path to the file.
    :param chunk: Maximum number of bytes to sample from the beginning of the file.
    :param strict: If True, raise EncodingDetectionError when detection returns no match.
    :return: The detected encoding name as a string.
    """
    with open(file_path, "rb") as file:
        data_sample = file.read(chunk)
        extra = file.read(1)

    if not data_sample:
        return "utf-8"

    # 1. Check BOM first
    if data_sample.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if data_sample.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        return "utf-32"
    if data_sample.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"

    # 2. Trim at the last newline when file was truncated by chunk so multibyte characters aren't split
    if extra:
        last_nl = max(data_sample.rfind(b"\n"), data_sample.rfind(b"\r"))
        if last_nl > 0:
            data_sample = data_sample[: last_nl + 1]

    # 3. Run charset_normalizer.from_bytes(...).best()
    best = charset_normalizer.from_bytes(data_sample).best()
    if best is None or not best.encoding:
        if strict:
            raise EncodingDetectionError(f"Could not detect encoding for '{file_path}'")
        return "utf-8"

    detected = best.encoding.lower()

    # 4. Heuristic: if iso-8859-1 / latin-1 / latin_1 / iso8859-1 and sample has 0x80..0x9F bytes, upgrade to cp1252
    if detected in {"iso-8859-1", "iso_8859_1", "iso8859-1", "iso8859_1", "latin-1", "latin_1", "latin1"}:
        if _has_c1_control_bytes(data_sample):
            return "cp1252"

    return detected


def detect_delimiter(
    file_path: str | os.PathLike,
    encoding: str | None = "utf-8",
) -> str:
    """
    Detects the most likely delimiter in a CSV file using csv.Sniffer with header-count fallback.

    :param file_path: The path to the file.
    :param encoding: The encoding to use when reading the file (auto-detected if None).
    :return: The detected delimiter character (one of ',', ';', '\\t', '|').
    """
    possible_delimiters = [",", ";", "\t", "|"]
    detected_delimiter = ","

    effective_encoding = encoding or detect_encoding(file_path)

    try:
        with open(file_path, "r", encoding=effective_encoding, errors="replace", newline="") as f:
            lines = []
            for _ in range(20):
                line = f.readline()
                if not line:
                    break
                lines.append(line)

        if not lines:
            return detected_delimiter

        sample = "".join(lines)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="".join(possible_delimiters))
            if dialect.delimiter in possible_delimiters:
                return dialect.delimiter
        except csv.Error:
            pass

        first_line = lines[0]
        counts = {d: first_line.count(d) for d in possible_delimiters}
        if any(c > 0 for c in counts.values()):
            detected_delimiter = max(counts, key=lambda d: counts[d])
    except Exception as e:
        logger.warning(f"Could not detect delimiter for {os.path.basename(file_path)}: {e}")

    return detected_delimiter

def _sanitize_table_name(stem: str, used_names: set[str]) -> str:
    """Create a valid, collision-free SQL table identifier from a filename stem."""
    base = re.sub(r"[^a-zA-Z0-9_]", "_", stem)
    if not base:
        base = "t_"
    elif base[0].isdigit():
        base = f"t_{base}"

    candidate = base
    counter = 2
    while candidate in used_names:
        candidate = f"{base}_{counter}"
        counter += 1

    used_names.add(candidate)
    return candidate


def process_files(
    directory_path: str | os.PathLike,
    recursive: bool = False,
) -> list[dict]:
    """
    Scans CSV files in a directory, detects their encoding and delimiter, and returns metadata.

    :param directory_path: Path to the directory to scan.
    :param recursive: If True, scan subdirectories recursively.
    :return: A sorted list of dictionaries containing metadata for each CSV file.
    """
    dir_path = Path(directory_path)
    if not dir_path.is_dir():
        logger.warning(f"Error: The directory '{directory_path}' does not exist.")
        return []

    iterator = dir_path.rglob("*") if recursive else dir_path.iterdir()
    csv_files = sorted(
        (p for p in iterator if p.is_file() and p.suffix.lower() == ".csv"),
        key=lambda p: str(p.relative_to(dir_path)),
    )

    results = []
    used_names: set[str] = set()

    for file_path_obj in csv_files:
        filename = file_path_obj.name
        file_path = str(file_path_obj)

        python_encoding = detect_encoding(file_path)
        delimiter = detect_delimiter(file_path, encoding=python_encoding)
        resolution = resolve_encoding(python_encoding)
        duckdb_encoding = get_duckdb_encoding(python_encoding)
        table_name = _sanitize_table_name(file_path_obj.stem, used_names)

        results.append({
            "filename": filename,
            "path": file_path,
            "python_encoding": python_encoding,
            "duckdb_encoding": duckdb_encoding,
            "delimiter": delimiter,
            "table_name": table_name,
            "resolution": resolution,
        })

    return results

def write_utf8_csv(
    src: str | os.PathLike,
    dst: str | os.PathLike,
    source_encoding: str | None = None,
    errors: str = "strict",
) -> Path:
    """
    Transcodes a CSV file from its source encoding to UTF-8 without modifying line endings.

    :param src: Path to the source CSV file.
    :param dst: Path where the UTF-8 encoded CSV will be saved (must differ from src).
    :param source_encoding: Source encoding name (auto-detected if None).
    :param errors: Error handling scheme passed to open() (default: 'strict').
    :return: The destination Path.
    """
    src_path = Path(src)
    dst_path = Path(dst)

    if src_path.resolve() == dst_path.resolve():
        raise ValueError("Destination path must not be the same as source path.")
    if dst_path.exists() and src_path.exists() and os.path.samefile(src_path, dst_path):
        raise ValueError("Destination path must not be the same file as source path.")

    enc = source_encoding or detect_encoding(src_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_size = 64 * 1024
    with (
        open(src_path, "r", encoding=enc, errors=errors, newline="") as infile,
        open(dst_path, "w", encoding="utf-8", errors=errors, newline="") as outfile,
    ):
        while True:
            block = infile.read(chunk_size)
            if not block:
                break
            outfile.write(block)

    return dst_path


def resolve_encoding(name: str | None, con=None, install_extension: bool = False):
    """Resolve a Python encoding name for DuckDB."""
    return get_duckdb_encoding(name or "utf-8")
