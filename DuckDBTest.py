import duckdb
import os
from charset_normalizer import from_path

# --- CONFIGURAÇÃO ---
path = "csv_encodings"

# --- CONEXÃO COM O DUCKDB ---
con = duckdb.connect(database=":memory:")
con.execute("INSTALL encodings;")
con.execute("LOAD encodings;")

# --- LOOP SOBRE OS ARQUIVOS CSV ---
for arquivo in os.listdir(path):
    if not arquivo.endswith(".csv"):
        continue

    caminho_arquivo = os.path.join(path, arquivo)
    nome_tabela = os.path.splitext(arquivo)[0]  # remove o .csv do final

    # --- DETECTAR ENCODING ---
    resultado_charset = from_path(caminho_arquivo)
    if resultado_charset is None:
        print(f"❌ Não foi possível detectar encoding para {arquivo}")
        continue

    encoding_detectado = resultado_charset.encoding
    print(f"\n📂 Arquivo: {arquivo}")
    print(f"🔍 Encoding detectado: {encoding_detectado}")

    # --- TENTAR INSERIR NO DUCKDB ---
    try:
        query = f"""
            CREATE OR REPLACE TEMP TABLE "{nome_tabela}" AS
            SELECT * FROM read_csv('{caminho_arquivo}', encoding='{encoding_detectado}', AUTO_DETECT=TRUE)
        """
        con.execute(query)
        print(f"✅ Sucesso ao carregar {arquivo} como tabela '{nome_tabela}'")

    except Exception as e:
        print(f"❌ Falha ao carregar {arquivo} com encoding '{encoding_detectado}': {e}")

# --- OPCIONAL: LISTAR TABELAS CARREGADAS ---
print("\n--- Tabelas temporárias criadas no DuckDB ---")
print(con.execute("SHOW TABLES").fetchall())
