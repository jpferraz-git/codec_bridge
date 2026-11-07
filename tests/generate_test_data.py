import csv
import os
from pathlib import Path

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "assets")

SPECIAL_SAMPLES: dict[str, str] = {
    "utf-8": "Informação de configuração: ação, coração, café, preço €10, “aspas curvas” 🚀",
    "utf-8-sig": "Informação de configuração: ação, coração, café, preço €10, “aspas curvas”",
    "utf-16": "Informação de configuração: ação, coração, café, preço €10, “aspas curvas”",
    "iso-8859-1": "Informação de configuração em português: ação, coração, irmã, café, avó, ç, ã, é",
    "windows-1252": "Relatório financeiro em português: ação, coração, irmã, café, €150, “aspas curvas”",
    "cp1252": "Relatório financeiro em português: ação, coração, irmã, café, €150, “aspas curvas”",
    "ascii": "Standard ASCII configuration record without accented characters",
    "iso-8859-2": "Zażółć gęślą jaźń oraz śćźżńłóę w raporcie centralnym",
    "iso-8859-5": "Проверка кодировки кириллицы в файле данных ДЖЙЩЮЯ",
    "koi8-r": "Проверка кодировки кириллицы в файле данных ДЖЙЩЮЯ",
    "shift_jis": "日本語のテストデータ文字列・シフトJISエンコーディング確認・アイウエオ",
    "gbk": "中文测试数据字符串用于验证字符编码检测与数据库读取你好世界",
    "big5": "繁體中文測試資料字串用於驗證字元編碼檢測與資料庫讀取你好世界",
    "windows-1253": "Δοκιμή ελληνικής κωδικοποίησης χαρακτήρων αβγδεζηθ",
    "iso-8859-15": "Informação em português com símbolo do euro: ação, coração, café, €200",
}


def create_encoded_csv(
    path: str | os.PathLike,
    encoding: str,
    delimiter: str = ",",
    min_bytes: int = 22 * 1024,
    sample_text: str | None = None,
) -> tuple[Path, list[tuple[str, str, str]]]:
    """
    Create a CSV file encoded with `encoding` and at least `min_bytes` in size.
    Returns (file_path, expected_rows).
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    phrase = sample_text or SPECIAL_SAMPLES.get(encoding.lower(), "Sample text for encoding test")

    rows: list[tuple[str, str, str]] = []
    idx = 0
    # Build enough rows to exceed min_bytes
    approx_row_bytes = len((f"{idx}{delimiter}{phrase}{delimiter}val_{idx}\n").encode(encoding))
    target_rows = max(20, (min_bytes // max(approx_row_bytes, 1)) + 5)

    for idx in range(target_rows):
        rows.append((f"id_{idx}", f"{phrase} #{idx}", f"metric_{idx}"))

    with open(out_path, mode="w", encoding=encoding, newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(["id", "description", "metric"])
        writer.writerows(rows)

    return out_path, rows


def generate_csv_test_files(
    output_dir: str | os.PathLike = DEFAULT_OUTPUT_DIR,
    min_bytes: int = 22 * 1024,
) -> dict[str, Path]:
    """
    Generate a suite of CSV files across multiple encodings for testing.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated: dict[str, Path] = {}
    for enc in SPECIAL_SAMPLES:
        file_path = Path(output_dir) / f"test_{enc}.csv"
        create_encoded_csv(file_path, encoding=enc, min_bytes=min_bytes)
        generated[enc] = file_path
    return generated


if __name__ == "__main__":
    generate_csv_test_files()
