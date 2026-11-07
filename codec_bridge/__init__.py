from importlib.metadata import PackageNotFoundError, version

from codec_bridge.encoding_translator import (
    EncodingDetectionError,
    detect_delimiter,
    detect_encoding,
    get_duckdb_encoding,
    process_files,
    resolve_encoding,
    write_utf8_csv,
)

try:
    __version__ = version("codec_bridge")
except PackageNotFoundError:
    __version__ = "0.2.5"

__all__ = [
    "EncodingDetectionError",
    "__version__",
    "detect_delimiter",
    "detect_encoding",
    "get_duckdb_encoding",
    "process_files",
    "resolve_encoding",
    "write_utf8_csv",
]
