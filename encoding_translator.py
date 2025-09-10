import charset_normalizer
import os
import re
from Repository.PythonToDuckDB import PYTHON_TO_DUCKDB_ENCODING
from tests.duckdb_utils import create_table_from_csv
import charset_normalizer
import os
import re
from Repository.PythonToDuckDB import PYTHON_TO_DUCKDB_ENCODING
from tests.duckdb_utils import create_table_from_csv

class EncodingDetect:
    def __init__(self, path: str):
        """
        Inicializa a instância com o caminho do diretório a ser processado.
        """
        self.path = path
        self.resultados = []

    def get_duckdb_encoding(self, python_encoding_name: str) -> str:
        """
        Traduz um nome de encoding do Python para o nome esperado pelo DuckDB.
        Se não encontrar um mapeamento, retorna o nome original como fallback.
        """
        if not python_encoding_name:
            return 'utf-8'  # Fallback seguro

        normalized_name = python_encoding_name.lower()
        return PYTHON_TO_DUCKDB_ENCODING.get(normalized_name, python_encoding_name)

    def detect_encoding(self, file_path: str) -> str:
        """
        Detecta o encoding de um arquivo usando charset_normalizer.
        """
        with open(file_path, "rb") as file:
            data = file.read(1000000)
            result = charset_normalizer.detect(data)
            return result.get("encoding") if result else "utf-8"

    def detect_delimiter(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Detecta o delimitador mais provável com base na primeira linha do arquivo.
        """
        delimitadores_possiveis = [',', ';', '\t', '|']
        delimitador_final = ','

        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                primeira_linha = f.readline()
                counts = {d: primeira_linha.count(d) for d in delimitadores_possiveis}
                if any(c > 0 for c in counts.values()):
                    delimitador_final = max(counts, key=counts.get)
        except Exception as e:
            print(f"[WARN] Não foi possível detectar o delimitador para {os.path.basename(file_path)}: {e}")

        return delimitador_final

    def process_files(self) -> list[dict]:
        """
        Percorre todos os arquivos CSV no diretório da instância e coleta metadados.
        """
        if not os.path.isdir(self.path):
            print(f"Erro: O diretório '{self.path}' não existe.")
            return []

        for f in os.listdir(self.path):
            if not f.lower().endswith('.csv'):
                continue

            file_path = os.path.join(self.path, f)
            print("-" * 50)

            python_encoding = self.detect_encoding(file_path)
            delimitador = self.detect_delimiter(file_path, encoding=python_encoding)
            duckdb_encoding = self.get_duckdb_encoding(python_encoding)
            table_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(f)[0])

            self.resultados.append({
                "arquivo": f,
                "caminho": file_path,
                "encoding_python": python_encoding,
                "encoding_duckdb": duckdb_encoding,
                "delimitador": delimitador,
                "nome_tabela": table_name
            })

        return self.resultados


if __name__ == "__main__":
    import duckdb

    path_dos_csvs = "csv_encodings"

    conn = duckdb.connect(database=":memory:")
    conn.execute("INSTALL encodings")
    conn.execute("LOAD encodings")

    detector = EncodingDetect(path_dos_csvs)
    resultados = detector.process_files()

    for resultado in resultados:
        create_table_from_csv(
            conn,
            resultado["caminho"],
            resultado["nome_tabela"],
            resultado["delimitador"],
            resultado["encoding_duckdb"]
        )

    conn.close()