import charset_normalizer
import duckdb
import os
import re
from Repository.PythonToDuckDB import PYTHON_TO_DUCKDB_ENCODING

def get_duckdb_encoding(python_encoding_name: str) -> str:
    """
    Traduz um nome de encoding do Python para o nome esperado pelo DuckDB.
    Se não encontrar um mapeamento, retorna o nome original como fallback.
    """
    if not python_encoding_name:
        return 'utf-8'  # Um fallback seguro

    normalized_name = python_encoding_name.lower()
    return PYTHON_TO_DUCKDB_ENCODING.get(normalized_name, python_encoding_name)

# ==============================================================================
# MÓDULO DE LÓGICA
# ==============================================================================

def detect_encoding(file_path: str) -> str:
    """
    Detecta o encoding de um arquivo usando charset_normalizer.
    """
    with open(file_path, "rb") as file:
        data = file.read(1000000)
        result = charset_normalizer.detect(data)
        return result.get("encoding") if result else "utf-8"

def detect_delimiter(file_path: str, encoding: str = "utf-8") -> str:
    """
    Detecta o delimitador mais provável com base na primeira linha do arquivo.
    Pode receber um encoding específico, ou usar o padrão 'utf-8'.
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


def create_table_from_csv(conn, file_path: str, table_name: str, delimiter: str, encoding: str):
    """
    Cria uma tabela no DuckDB a partir de um CSV, usando os parâmetros corretos.
    """
    print(
        f"Processando '{os.path.basename(file_path)}': Tabela='{table_name}', Encoding='{encoding}', Delim='{delimiter}'")
    try:
        conn.sql(f"""
                CREATE OR REPLACE TABLE "{table_name}" AS
                (SELECT * FROM 
                read_csv('{file_path}',
                delim='{delimiter}',
                encoding='{encoding}',
                header=true,
                auto_detect=true
                ) LIMIT 1000)
                """)
        print(f"✅ Tabela '{table_name}' criada com sucesso.")
        print(conn.sql(f'SELECT * FROM "{table_name}" LIMIT 3'))
    except Exception as e:
        print(f"❌ ERRO ao criar a tabela '{table_name}': {e}")


def process_files_in_directory(path: str, conn):
    """
    Função principal que orquestra o processo para todos os arquivos em um diretório.
    """
    if not os.path.isdir(path):
        print(f"Erro: O diretório '{path}' não existe.")
        return

    for f in os.listdir(path):
        if not f.lower().endswith('.csv'):
            continue

        file_path = os.path.join(path, f)
        print("-" * 50)

        python_encoding = detect_encoding(file_path)
        delimitador = detect_delimiter(file_path, encoding=python_encoding)
        duckdb_encoding = get_duckdb_encoding(python_encoding)

        # 3. Cria um nome de tabela dinâmico a partir do nome do arquivo
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(f)[0])

        # 4. Chama a função para criar a tabela com os parâmetros corretos e traduzidos
        create_table_from_csv(conn, file_path, table_name, delimitador, duckdb_encoding)

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    path_dos_csvs = "csv_encodings"  # Usando o diretório dos testes anteriores

    # Prepara a conexão com o DuckDB
    conn = duckdb.connect(database=":memory:")
    conn.execute("INSTALL encodings")  # A extensão correta é 'icu'
    conn.execute("LOAD encodings")

    # Inicia o processamento
    process_files_in_directory(path_dos_csvs, conn)