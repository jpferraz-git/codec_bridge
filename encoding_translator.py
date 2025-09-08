import charset_normalizer
from charset_normalizer import detect
import duckdb
import os
import re
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
#
# PYTHON_TO_DUCKDB_ENCODING = {
#     # --- Encodings Globais e Comuns ---
#     'utf-8': 'UTF-8',
#     'utf-16': 'UTF-16',
#     'utf-16-be': 'UTF-16BE',
#     'utf-16-le': 'UTF-16LE',
#     'ascii': 'US-ASCII',
#
#     # --- Encodings Europeus Ocidentais (Latino) ---
#     # ISO-8859-1 (Latin-1) corresponde à página de código IBM 819 no padrão ICU.
#     # DuckDB também costuma aceitar o alias 'LATIN1'.
#     'iso-8859-1': 'ibm-819',
#     'latin-1': 'ibm-819', # Adicionando alias comum
#
#     'windows-1252': 'windows-1252',
#     'cp1252': 'windows-1252', # Adicionando alias comum
#
#     # ISO-8859-15 (Latin-9) é a página de código IBM 923.
#     'iso-8859-15': 'ibm-923',
#
#     # --- Encodings do Leste Asiático ---
#     'shift_jis': 'shift_jis',       # Japonês
#     'euc-jp': 'EUC-JP',          # Japonês
#     'gbk': 'GBK',                # Chinês Simplificado
#     'gb2312': 'GB2312',          # Chinês Simplificado
#     'euc-kr': 'EUC-KR',          # Coreano
#
#     # --- Encodings Cirílicos ---
#     'iso-8859-5': 'ibm-915',
#     'windows-1251': 'windows-1251',
#     'cp1251': 'windows-1251' # Adicionando alias comum
# }

# fast_encoding/mapper.py

# ==============================================================================
# DICIONÁRIO 1: O "TRADUTOR DE BAGUNÇA"
# Mapeia todos os aliases conhecidos para um nome canônico interno e limpo.
# A chave é sempre em minúsculas para normalizar a entrada.
# ==============================================================================
PYTHON_TO_DUCKDB_ENCODING = {
    # --- Conceito: UTF-8 (O Padrão Absoluto) ---
    'utf_8': 'utf-8',
    'utf8': 'utf_8',

    # --- Conceito: UTF-16 ---
    'utf_16': 'utf-16',
    'utf_16be': 'utf_16_be',  # Big Endian
    'utf_16le': 'utf_16_le',  # Little Endian

    # --- Conceito: ASCII ---
    'ascii': 'ascii',
    'us-ascii': 'ascii',
    'ibm-367_p100-1995': 'ascii',
    'iso-ir-6': 'ascii',

    # --- Conceito: Latin-1 (Europa Ocidental) ---
    'latin-1': 'latin_1',
    'latin1': 'latin_1',
    'iso-8859-1': 'latin_1',
    'iso_8859_1': 'latin_1',
    'ibm-819': 'latin_1',
    'cp819': 'latin_1',
    'iso8859_1': 'latin_1',
    'iso8859_14': 'ISO_8859_14',
    'iso8859_10': 'ISO_8859_10',
    # --- Conceito: Windows-1252 (Superconjunto do Latin-1) ---
    'windows-1252': 'ISO8859_1',
    'cp1252': 'windows_1252',

    # --- Conceito: Latin-2 (Europa Central/Oriental) ---
    'iso-8859-2': 'latin_2',
    'iso_8859_2': 'latin_2',
    'latin-2': 'latin_2',
    'latin2': 'latin_2',
    'windows-1250': 'CP1250',  # Variação Windows do Latin-2
    'cp1250': 'windows_1250',
    'cp852': 'cp852',
    "mac_iceland": "MAC_IS",# Variação DOS do Latin-2

    # --- Conceito: Cirílico ---
    'iso-8859-5': 'iso_8859_5',
    'iso_8859_5': 'iso_8859_5',
    'cyrillic': 'iso_8859_5',
    'windows-1251': 'windows_1251',
    'cp1251': 'windows_1251',
    'koi8-r': 'koi8_r',  # Outro padrão russo popular
    'koi8_r': 'koi8_r',

    # --- Conceito: Grego ---
    'iso-8859-7': 'iso_8859_7',
    'iso_8859_7': 'iso_8859_7',
    'windows-1253': 'windows_1253',
    'cp1253': 'windows_1253',

    # --- Conceito: Japonês ---
    'shift_jis': 'shift_jis',
    'sjis': 'shift_jis',
    'ibm-943': 'shift_jis',
    'windows-932': 'shift_jis',
    'euc-jp': 'euc_jp',

    # --- Conceito: Chinês ---
    'gbk': 'gbk',
    'gb2312': 'gb2312',
    'big5': 'big5',

    # --- Conceito: Coreano ---
    'euc-kr': 'euc_kr',
    'cp949': 'cp949',
    'johab': 'johab',
}

# ==============================================================================
# DICIONÁRIO 2: O "TRADUTOR ORGANIZADO"
# Mapeia nosso nome canônico limpo para o nome específico de cada ferramenta.
# ==============================================================================
MAPA_CANONICO_PARA_ALVO = {
    'utf_8': {
        'python': 'utf-8',
        'duckdb': 'UTF-8',
        'spark': 'UTF-8',
        'pandas': 'utf-8',
        'polars': 'utf8',
        'postgres': 'UTF8',
    },
    'latin_1': {
        'python': 'iso-8859-1',
        'duckdb': 'ibm-819',  # Nome canônico ICU para ISO-8859-1
        'spark': 'ISO-8859-1',
        'pandas': 'iso-8859-1',
        'polars': 'latin1',
        'postgres': 'LATIN1',
    },
    'windows_1252': {
        'python': 'windows-1252',
        'duckdb': 'windows-1252',
        'spark': 'Windows-1252',
        'pandas': 'cp1252',
        'polars': 'windows-1252',
        'postgres': 'WIN1252',
    },
    'windows_1250': {
        'python': 'windows-1250',
        'duckdb': 'windows-1250-2000',  # Nome completo do ICU
        'spark': 'Windows-1250',
        'pandas': 'cp1250',
        'polars': 'windows-1250',
        'postgres': 'WIN1250',
    },
    'shift_jis': {
        'python': 'shift_jis',
        'duckdb': 'shift_jis',
        'spark': 'Shift_JIS',
        'pandas': 'shift_jis',
        'polars': 'shift-jis',
        'postgres': 'SJIS',
    },
    # ... Adicionar outros mapeamentos seguindo a mesma lógica
}


def get_duckdb_encoding(python_encoding_name: str) -> str:
    """
    Traduz um nome de encoding do Python para o nome esperado pelo DuckDB.
    Se não encontrar um mapeamento, retorna o nome original como fallback.
    """
    if not python_encoding_name:
        return 'UTF-8'  # Um fallback seguro

    normalized_name = python_encoding_name.lower()
    return PYTHON_TO_DUCKDB_ENCODING.get(normalized_name, python_encoding_name)


# ==============================================================================
# MÓDULO DE LÓGICA
# ==============================================================================

def detect_properties(file_path: str) -> tuple[str | None, str]:
    """
    Função Helper que detecta tanto o encoding quanto o delimitador de um arquivo.
    """
    # 1. Detectar Encoding
    with open(file_path, "rb") as file:
        data = file.read(100000)  # Ler um chunk para detecção
        result = charset_normalizer.detect(data)
        python_encoding = result.get("encoding") if result else "utf-8"

    # 2. Detectar Delimitador (Lógica melhorada)
    delimitadores_possiveis = [',', ';', '\t', '|']
    delimitador_final = ','  # Default seguro

    try:
        with open(file_path, 'r', encoding=python_encoding, errors='replace') as f:
            primeira_linha = f.readline()

            # Lógica mais robusta: encontra o delimitador com a maior contagem
            counts = {d: primeira_linha.count(d) for d in delimitadores_possiveis}
            if any(c > 0 for c in counts.values()):
                delimitador_final = max(counts, key=counts.get)

    except Exception as e:
        print(f"[WARN] Não foi possível detectar o delimitador para {os.path.basename(file_path)}: {e}")

    return python_encoding, delimitador_final


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

        # 1. Detecta as propriedades do arquivo (encoding Python e delimitador)
        python_encoding, delimitador = detect_properties(file_path)

        # 2. **A MÁGICA ACONTECE AQUI: TRADUZ O ALIAS!**
        # Pega o encoding detectado (ex: 'iso-8859-1') e traduz para o que o DuckDB espera (ex: 'ibm-819')
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
    conn.execute("INSTALL icu")  # A extensão correta é 'icu'
    conn.execute("LOAD icu")

    # Inicia o processamento
    process_files_in_directory(path_dos_csvs, conn)





