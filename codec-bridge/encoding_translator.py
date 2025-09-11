import charset_normalizer
import os
import re

# Project-specific modules
from Repository.python_to_duckdb import PYTHON_TO_DUCKDB_ENCODING

class EncodingDetector:
    """
    A class to detect encoding and delimiter for files within a directory,
    and provide metadata for processing with data tools like DuckDB.
    """

    def __init__(self, directory_path: str):
        """
        Initializes the instance with the path to the directory to be processed.

        :param directory_path: The path to the folder containing CSV files.
        """
        self.directory_path = directory_path
        self.results = []

    def get_duckdb_encoding(self, python_encoding_name: str) -> str:
        """
        Translates a Python-standard encoding name to the name expected by DuckDB.
        If no specific mapping is found, it returns the original name as a fallback.

        :param python_encoding_name: The encoding name detected (e.g., 'iso-8859-1').
        :return: The translated encoding name for DuckDB (e.g., 'ibm-819').
        """
        if not python_encoding_name:
            return 'utf-8'

        normalized_name = python_encoding_name.lower()
        return PYTHON_TO_DUCKDB_ENCODING.get(normalized_name, python_encoding_name)

    def detect_encoding(self, file_path: str) -> str:
        """
        Detects the character encoding of a file using charset_normalizer.

        :param file_path: The full path to the file.
        :return: The detected encoding name as a string.
        """
        with open(file_path, "rb") as file:
            data_sample = file.read(1000000)
            result = charset_normalizer.detect(data_sample)
            return result.get("encoding") if result else "utf-8"

    def detect_delimiter(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Detects the most likely delimiter based on the first line of the file.

        :param file_path: The full path to the file.
        :param encoding: The encoding to use when reading the file.
        :return: The detected delimiter character.
        """
        possible_delimiters = [',', ';', '\t', '|']
        detected_delimiter = ','  # Default to comma

        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                first_line = f.readline()
                # Find the delimiter with the highest count in the header line
                counts = {d: first_line.count(d) for d in possible_delimiters}
                if any(c > 0 for c in counts.values()):
                    detected_delimiter = max(counts, key=counts.get)
        except Exception as e:
            print(f"[WARN] Could not detect delimiter for {os.path.basename(file_path)}: {e}")

        return detected_delimiter

    def process_files(self) -> list[dict]:
        """
        Iterates through all CSV files in the instance's directory, detects their
        properties (encoding, delimiter), and stores them as metadata.

        This method acts as a utility to scan and prepare a batch of files.

        :return: A list of dictionaries, each containing metadata for a file.
        """
        if not os.path.isdir(self.directory_path):
            print(f"Error: The directory '{self.directory_path}' does not exist.")
            return []

        for filename in os.listdir(self.directory_path):
            if not filename.lower().endswith('.csv'):
                continue

            file_path = os.path.join(self.directory_path, filename)

            # Detect properties
            python_encoding = self.detect_encoding(file_path)
            delimiter = self.detect_delimiter(file_path, encoding=python_encoding)

            # Translate encoding for the target tool
            duckdb_encoding = self.get_duckdb_encoding(python_encoding)

            # Sanitize filename to create a valid table name
            table_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(filename)[0])

            self.results.append({
                "filename": filename,
                "path": file_path,
                "python_encoding": python_encoding,
                "duckdb_encoding": duckdb_encoding,
                "delimiter": delimiter,
                "table_name": table_name
            })

        return self.results


# if __name__ == "__main__":
#     import duckdb
#
#     csv_directory_path = "/home/user/Documentos/dadosGravados/Carga_11-24"
#
#     connection = duckdb.connect(database=":memory:")
#
#     # connection.execute("INSTALL icu")
#     # connection.execute("LOAD icu")
#
#     detector = EncodingDetector(csv_directory_path)
#
#     file_results = detector.process_files()
#
#     for result in file_results:
#         create_table_from_csv(
#             conn=connection,
#             file_path=result["path"],
#             table_name=result["table_name"],
#             delimiter=result["delimiter"],
#             encoding=result["duckdb_encoding"]
#         )
#
#     connection.close()