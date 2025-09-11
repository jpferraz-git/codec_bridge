# file: tests/generate_test_data.py

import csv
import os


DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "assets")

def generate_csv_test_files(output_dir: str = DEFAULT_OUTPUT_DIR, num_rows: int = 100):
    """
    Generates a suite of CSV files with different encodings and characters
    to be used as assets for running tests.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating test files in: {output_dir}")

    encodings_to_test = [
        "utf-8", "utf-16", "iso-8859-1", "windows-1252",
        "ascii", "iso-8859-2", "iso-8859-5", "koi8-r",
        "shift_jis", "gbk", "big5", "windows-1253", "iso-8859-15"
    ]

    # Dictionary of "killer characters" to make each encoding unique
    special_chars = {
        "iso-8859-1": "ç",
        "windows-1252": "€",
        "iso-8859-2": "ść",
        "iso-8859-5": "ДЖ",
        "koi8-r": "ДЖ",
        "shift_jis": "ア",
        "gbk": "你好",
        "big5": "你好",
        "windows-1253": "αβ",
        "iso-8859-15": "€",
        "utf-8": "🚀",
        "utf-16": "🚀",
    }

    def generate_rows(example_char=""):
        # Add the special character to the first cell of each row
        return [[f"Data_{i}_{j}{example_char if j == 0 else ''}" for j in range(5)] for i in range(num_rows)]

    # Loop through encodings and generate files
    for enc in encodings_to_test:
        filename = os.path.join(output_dir, f"test_{enc}.csv")
        special_char = special_chars.get(enc, "")
        rows = generate_rows(special_char)

        try:
            with open(filename, mode="w", encoding=enc, newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Header_1", "Header_2", "Header_3", "Header_4", "Header_5"])
                writer.writerows(rows)
            print(f"✅ Generated: {os.path.basename(filename)} (with char: '{special_char}')")
        except UnicodeEncodeError:
            print(f"❌ Encoding Error with {enc}: The character '{special_char}' is not supported.")
        except Exception as e:
            print(f"⚠️ Unexpected Error with {enc}: {e}")

if __name__ == "__main__":
    # This allows you to run the script directly to generate the files
    # python tests/generate_test_data.py
    generate_csv_test_files()