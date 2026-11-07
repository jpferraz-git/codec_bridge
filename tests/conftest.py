from pathlib import Path
import duckdb
import pytest

from tests.generate_test_data import create_encoded_csv


@pytest.fixture
def duckdb_con():
    """Provide an isolated in-memory DuckDB connection without extensions preloaded."""
    con = duckdb.connect(":memory:")
    try:
        yield con
    finally:
        con.close()


@pytest.fixture
def duckdb_ext():
    """
    Provide an in-memory DuckDB connection with the 'encodings' extension installed and loaded.
    Skips the test if installing or loading the extension fails (e.g., offline environment).
    """
    con = duckdb.connect(":memory:")
    try:
        con.execute("INSTALL encodings; LOAD encodings;")
    except Exception as exc:
        con.close()
        pytest.skip(f"DuckDB encodings extension is unavailable: {exc}")

    try:
        yield con
    finally:
        con.close()


@pytest.fixture
def make_encoded_csv(tmp_path: Path):
    """
    Factory fixture that creates a >=20 KB CSV file for a requested encoding and delimiter,
    returning (file_path, expected_rows).
    """
    counter = 0

    def _make(
        encoding: str,
        delimiter: str = ",",
        min_bytes: int = 22 * 1024,
        sample_text: str | None = None,
        filename: str | None = None,
    ) -> tuple[Path, list[tuple[str, str, str]]]:
        nonlocal counter
        counter += 1
        safe_enc = encoding.replace("/", "_")
        target = tmp_path / (filename or f"sample_{counter}_{safe_enc}.csv")
        return create_encoded_csv(
            target,
            encoding=encoding,
            delimiter=delimiter,
            min_bytes=min_bytes,
            sample_text=sample_text,
        )

    return _make
