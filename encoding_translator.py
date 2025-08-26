import chardet
import charset_normalizer
from charset_normalizer import detect
import duckdb
import os
ENCODING_ALIASES = {
    # Chave é o nome padrão que o chardet/python usa
    'iso-8859-1': {
        'python': 'iso-8859-1',
        'duckdb': 'latin1',
        'spark': 'LATIN1',
    },
    'windows-1252': {
        'python': 'windows-1252',
        'duckdb': 'latin1', # DuckDB trata como latin1
        'spark': 'Windows-1252', # Spark tem case-sensitive aqui
    },
    'utf-8': {
        'python': 'utf-8',
        'duckdb': 'UTF8', # DuckDB prefere assim
        'spark': 'UTF-8',
    },
    # Adicionar outros mapeamentos comuns...
}

def get_alias(encoding_name: str, target_system: str) -> str | None:
    """
    Recebe um nome de encoding padrão e um sistema de destino,
    e retorna o alias correto para aquele sistema.
    """
    encoding_name = encoding_name.lower()
    if encoding_name in ENCODING_ALIASES:
        return ENCODING_ALIASES[encoding_name].get(target_system.lower())
    return None # Ou retorna o nome original como fallback

# Testes rápidos
# print(f"Para Spark, use: {get_alias('ISO-8859-1', 'spark')}")
# print(f"Para DuckDB, use: {get_alias('UTF-8', 'duckdb')}")

def read_encoding(path):
    with open(path, "rb") as file:
        data = file.read(10000)
        return detect(data)
#
# print(read_encoding("aaa.csv"))
# print(read_encoding("repository/10gb.csv"))
# print(read_encoding("repository/1gb.csv"))
# print(read_encoding("repository/100mb.csv"))
# print(read_encoding("repository/Assistidos_119_20241101.csv"))

PYTHON_TO_DUCKDB_ENCODING = {
    # --- Encodings Globais e Comuns ---
    'utf-8': 'UTF-8',
    'utf-16': 'UTF-16',
    'utf-16-be': 'UTF-16BE',
    'utf-16-le': 'UTF-16LE',
    'ascii': 'US-ASCII',

    # --- Encodings Europeus Ocidentais (Latino) ---
    # ISO-8859-1 (Latin-1) corresponde à página de código IBM 819 no padrão ICU.
    # DuckDB também costuma aceitar o alias 'LATIN1'.
    'iso-8859-1': 'ibm-819',
    'latin-1': 'ibm-819', # Adicionando alias comum

    'windows-1252': 'windows-1252',
    'cp1252': 'windows-1252', # Adicionando alias comum

    # ISO-8859-15 (Latin-9) é a página de código IBM 923.
    'iso-8859-15': 'ibm-923',

    # --- Encodings do Leste Asiático ---
    'shift_jis': 'shift_jis',       # Japonês
    'euc-jp': 'EUC-JP',          # Japonês
    'gbk': 'GBK',                # Chinês Simplificado
    'gb2312': 'GB2312',          # Chinês Simplificado
    'euc-kr': 'EUC-KR',          # Coreano

    # --- Encodings Cirílicos ---
    'iso-8859-5': 'ibm-915',
    'windows-1251': 'windows-1251',
    'cp1251': 'windows-1251' # Adicionando alias comum
}

def get_duckdb_encoding(python_encoding_name: str) -> str | None:
    """
    Função exemplo para obter o nome do encoding para o DuckDB
    a partir de um nome de encoding comum do Python, usando o dicionário simplificado.
    """
    # Normaliza o nome para minúsculas para a busca no dicionário
    normalized_name = python_encoding_name.lower()

    # Busca direta no dicionário
    return PYTHON_TO_DUCKDB_ENCODING.get(normalized_name, python_encoding_name)
    # O segundo argumento de .get() é o valor padrão a ser retornado se a chave não for encontrada.
    # Aqui, retornamos o próprio nome original como um fa

conn = duckdb.connect("/home/user/Documentos/testesIncremental/cargaIncremental.duckdb'")

def check_encodings(path):
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        with open(file_path, "rb") as file:
            data = file.read(1000000)
            encoding = charset_normalizer.detect(data)["encoding"]
            check_delim(file_path, encoding)

def check_delim(file_path, encoding):
    delimitadores_possiveis = [';', ',', '\t', '|']
    try:
        # Primeiro lê a primeira linha do arquivo para detectar o delimitador
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            primeira_linha = f.readline()

            delimitador = next((d for d in delimitadores_possiveis if primeira_linha.count(d) > 1), '|')

        # Depois, converte o arquivo para o novo delimitador
        # with open(caminho_origem, 'r', encoding=encoding, errors='replace') as origem, \
        #      open(caminho_destino, 'w', encoding='utf-8', newline='') as destino:
        #     leitor = csv.reader(origem, delimiter=delimitador)
        #     escritor = csv.writer(destino, delimiter='|')
        #     for linha in leitor:
        #         escritor.writerow(linha)
        create_table(file_path, delimitador, encoding)
        return delimitador

    except Exception as e:
        print(f"[WARN] Erro ao trocar delimitador: {e}")
        raise
def create_table(file, delimitador, encoding):
    # file = file.removesuffix(".csv")
    conn.sql(f"""
            CREATE OR REPLACE TABLE abacaxi AS
            (SELECT * FROM 
            read_csv('{file}',
            delim='{delimitador}',
            encoding='{encoding}'
            ) LIMIT 1000)
            """)

path = "/home/user/Documentos/encodingLibrary/ENCODING-ICU-Library/repository"
conn.execute("INSTALL encodings")
conn.execute("LOAD encodings")
check_encodings(path)





