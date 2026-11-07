from pathlib import Path
import charset_normalizer
import os
import re
import logging

from codec_bridge.repository.python_to_duckdb import PYTHON_TO_DUCKDB_ENCODING, ENCODINGS_UNDERSCORE_CONFLICT

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


def detect_delimiter(file_path: str, encoding: str = "utf-8") -> str:
    """
    Detects the most likely delimiter based on the first line of the file.

    :param file_path: The full path to the file.
    :param encoding: The encoding to use when reading the file.
    :return: The detected delimiter character.
    """
    possible_delimiters = [',', ';', '\t', '|']
    detected_delimiter = ','  # Default to comma
    if encoding.lower() in ENCODINGS_UNDERSCORE_CONFLICT:
        return '|'
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            first_line = f.readline()
            # Find the delimiter with the highest count in the header line
            counts = {d: first_line.count(d) for d in possible_delimiters}
            if any(c > 0 for c in counts.values()):
                detected_delimiter = max(counts, key=counts.get)
    except Exception as e:
        logger.warning(f" Could not detect delimiter for {os.path.basename(file_path)}: {e}")

    return detected_delimiter

def process_files(directory_path: str) -> list[dict]:
    """
    Iterates through all CSV files in the instance's directory, detects their
    properties (encoding, delimiter), and stores them as metadata.

    This method acts as a utility to scan and prepare a batch of files.

    :return: A list of dictionaries, each containing metadata for a file.
    """
    if not os.path.isdir(directory_path):
        logger.warning(f"Error: The directory '{directory_path}' does not exist.")
        return []

    results = []
    for filename in os.listdir(directory_path):
        if not filename.lower().endswith('.csv'):
            continue

        file_path = os.path.join(directory_path, filename)

        # Detect properties
        python_encoding = detect_encoding(file_path)
        delimiter = detect_delimiter(file_path, encoding=python_encoding)

        # Translate encoding for the target enconding case
        duckdb_encoding = get_duckdb_encoding(python_encoding)

        # Sanitize filename to create a valid table name
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(filename)[0])

        results.append({
            "filename": filename,
            "path": file_path,
            "python_encoding": python_encoding,
            "duckdb_encoding": duckdb_encoding,
            "delimiter": delimiter,
            "table_name": table_name
        })

    return results

def write_utf8_csv(file_path: str, new_csv_file_path: str):
    """
    Rewrites a CSV file using UTF-8 encoding.

    This method is intended for cases where, even after DuckDB's encoding detection,
    the file is still incorrectly interpreted when inserted into the database.

    :param file_path: Path to the original CSV file.
    :param new_csv_file_path: Path where the UTF-8 encoded CSV will be saved.
    :return: None. The UTF-8 encoded file is written to disk.
    """
    with open(file_path, 'r') as file:
        with open(new_csv_file_path, 'w', encoding='utf-8') as new_file:
            for line in file:
                new_file.write(line)


def resolve_encoding(name: str | None, con=None, install_extension: bool = False):
    """Resolve a Python encoding name for DuckDB."""
    return get_duckdb_encoding(name or "utf-8")
