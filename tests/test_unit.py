import logging
from pathlib import Path
import pytest

from codec_bridge import (
    EncodingDetectionError,
    EncodingResolution,
    UnsupportedEncodingError,
    detect_delimiter,
    detect_encoding,
    get_duckdb_encoding,
    normalize_name,
    process_files,
    resolve_encoding,
    write_utf8_csv,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, "utf-8"),
        ("", "utf-8"),
        ("   ", "utf-8"),
        ("UTF-8", "utf-8"),
        ("utf_8", "utf-8"),
        ("utf8", "utf-8"),
        ("UTF-8-SIG", "utf-8"),
        ("utf_8_sig", "utf-8"),
        ("latin1", "iso8859-1"),
        ("ISO-8859-1", "iso8859-1"),
        ("Windows-1252", "cp1252"),
        ("cp1252", "cp1252"),
        ("unknown_made_up_codec", "unknown_made_up_codec"),
    ],
)
def test_normalize_name(raw: str | None, expected: str):
    assert normalize_name(raw) == expected


def test_get_duckdb_encoding_supported_and_none():
    assert get_duckdb_encoding(None) == "utf-8"
    assert get_duckdb_encoding("") == "utf-8"
    assert get_duckdb_encoding("utf-8") == "utf-8"
    assert get_duckdb_encoding("UTF-8-SIG") == "utf-8"
    assert get_duckdb_encoding("cp1252") == "cp1252"
    assert get_duckdb_encoding("windows-1252") == "cp1252"


def test_get_duckdb_encoding_unknown_non_strict(caplog: pytest.LogCaptureFixture):
    with caplog.at_level(logging.WARNING):
        result = get_duckdb_encoding("unknown_codec_xyz", strict=False)
    assert result == "utf-8"
    assert "not mapped yet" in caplog.text


def test_get_duckdb_encoding_unknown_strict():
    with pytest.raises(UnsupportedEncodingError):
        get_duckdb_encoding("unknown_codec_xyz", strict=True)


@pytest.mark.parametrize("delim", [",", ";", "\t", "|"])
def test_detect_delimiter_basic(tmp_path: Path, delim: str):
    csv_file = tmp_path / "delim.csv"
    csv_file.write_text(f"col1{delim}col2{delim}col3\nval1{delim}val2{delim}val3\n", encoding="utf-8")
    assert detect_delimiter(csv_file) == delim


def test_detect_delimiter_quoted_fields(tmp_path: Path):
    csv_file = tmp_path / "quoted.csv"
    content = (
        'id;description;notes\n'
        '1;"item, with, many, commas";ok\n'
        '2;"another, comma, heavy, text";done\n'
    )
    csv_file.write_text(content, encoding="utf-8")
    assert detect_delimiter(csv_file) == ";"


def test_detect_delimiter_shift_jis_comma(make_encoded_csv):
    csv_path, _ = make_encoded_csv("shift_jis", delimiter=",")
    assert detect_delimiter(csv_path, encoding="shift_jis") == ","


def test_detect_delimiter_accepts_none_encoding(make_encoded_csv):
    csv_path, _ = make_encoded_csv("cp1252", delimiter=";")
    assert detect_delimiter(csv_path, encoding=None) == ";"


def test_detect_encoding_bom_variants(tmp_path: Path):
    f_utf8_sig = tmp_path / "bom_utf8.csv"
    f_utf8_sig.write_bytes("a,b\n1,2\n".encode("utf-8-sig"))
    assert detect_encoding(f_utf8_sig) == "utf-8-sig"

    f_utf16 = tmp_path / "bom_utf16.csv"
    f_utf16.write_bytes("a,b\n1,2\n".encode("utf-16"))
    assert detect_encoding(f_utf16) == "utf-16"

    f_utf32 = tmp_path / "bom_utf32.csv"
    f_utf32.write_bytes("a,b\n1,2\n".encode("utf-32"))
    assert detect_encoding(f_utf32) == "utf-32"


def test_detect_encoding_empty_and_strict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_bytes(b"")
    assert detect_encoding(empty_file) == "utf-8"

    sample_file = tmp_path / "sample.csv"
    sample_file.write_bytes(b"hello,world\n")

    class _DummyMatches:
        def best(self):
            return None

    monkeypatch.setattr("charset_normalizer.from_bytes", lambda _b: _DummyMatches())
    assert detect_encoding(sample_file, strict=False) == "utf-8"
    with pytest.raises(EncodingDetectionError):
        detect_encoding(sample_file, strict=True)


def test_write_utf8_csv_latin1_and_cp1252(tmp_path: Path, make_encoded_csv):
    latin1_src, _ = make_encoded_csv("iso-8859-1", filename="src_latin1.csv")
    latin1_dst = tmp_path / "dst_latin1.csv"
    ret = write_utf8_csv(latin1_src, latin1_dst)
    assert ret == latin1_dst
    assert latin1_dst.read_text(encoding="utf-8") == latin1_src.read_text(encoding="iso-8859-1")

    cp1252_src, _ = make_encoded_csv("cp1252", filename="src_cp1252.csv")
    cp1252_dst = tmp_path / "dst_cp1252.csv"
    write_utf8_csv(cp1252_src, cp1252_dst, source_encoding="cp1252")
    assert cp1252_dst.read_text(encoding="utf-8") == cp1252_src.read_text(encoding="cp1252")


def test_write_utf8_csv_preserves_crlf_and_prevents_overwrite(tmp_path: Path):
    src = tmp_path / "crlf.csv"
    raw_text = "id,name\r\n1,ação\r\n2,coração\r\n"
    src.write_bytes(raw_text.encode("iso-8859-1"))
    dst = tmp_path / "out_crlf.csv"

    write_utf8_csv(src, dst, source_encoding="iso-8859-1")
    assert dst.read_bytes() == raw_text.encode("utf-8")

    with pytest.raises(ValueError, match="Destination path must not be the same"):
        write_utf8_csv(src, src)


def test_write_utf8_csv_errors_parameter(tmp_path: Path):
    src = tmp_path / "bad_bytes.csv"
    src.write_bytes(b"id,text\n1,valid\n2,\xff\xfe\n")
    dst = tmp_path / "out_strict.csv"

    with pytest.raises(UnicodeDecodeError):
        write_utf8_csv(src, dst, source_encoding="utf-8", errors="strict")

    dst_replace = tmp_path / "out_replace.csv"
    write_utf8_csv(src, dst_replace, source_encoding="utf-8", errors="replace")
    assert "\ufffd" in dst_replace.read_text(encoding="utf-8")


def test_process_files_sorting_collisions_digits_and_uppercase(tmp_path: Path):
    # Create files testing:
    # 1. Name starting with digit ("2026_sales.csv" -> "t_2026_sales")
    # 2. Collision ("a-b.csv" and "a_b.CSV" -> "a_b" and "a_b_2")
    # 3. Uppercase extension (".CSV")
    # 4. Recursive subdirectory
    (tmp_path / "2026_sales.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "a-b.csv").write_text("a;b\n1;2\n", encoding="utf-8")
    (tmp_path / "a_b.CSV").write_text("a|b\n1|2\n", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("not a csv", encoding="utf-8")

    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "a_b.csv").write_text("a\tb\n1\t2\n", encoding="utf-8")

    non_rec = process_files(tmp_path, recursive=False)
    assert [item["filename"] for item in non_rec] == ["2026_sales.csv", "a-b.csv", "a_b.CSV"]
    assert [item["table_name"] for item in non_rec] == ["t_2026_sales", "a_b", "a_b_2"]
    for item in non_rec:
        assert isinstance(item["resolution"], EncodingResolution)

    rec = process_files(tmp_path, recursive=True)
    assert [item["filename"] for item in rec] == [
        "2026_sales.csv",
        "a-b.csv",
        "a_b.CSV",
        "a_b.csv",
    ]
    assert [item["table_name"] for item in rec] == [
        "t_2026_sales",
        "a_b",
        "a_b_2",
        "a_b_3",
    ]


def test_process_files_missing_directory(tmp_path: Path):
    assert process_files(tmp_path / "does_not_exist") == []


def test_resolve_encoding_native_and_transcode():
    res_utf8 = resolve_encoding("UTF-8-SIG")
    assert res_utf8 == EncodingResolution("utf-8", "utf-8", "native")

    res_latin1_clean = resolve_encoding("latin-1", has_c1_bytes=False)
    assert res_latin1_clean == EncodingResolution("iso8859-1", "latin-1", "native")

    res_utf16le = resolve_encoding("utf-16-le")
    assert res_utf16le == EncodingResolution("utf-16-le", None, "transcode")
