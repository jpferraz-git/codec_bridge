import duckdb
import pandas as pd
import requests
import re
import os


# --- PASSO 1: FUNÇÃO PARA OBTER A LISTA ---
def obter_lista_de_aliases_icu():
    url = 'https://raw.githubusercontent.com/duckdb/duckdb-encodings/main/src/icu_aliases.cpp'
    try:
        response = requests.get(url)
        response.raise_for_status()
        aliases = re.findall(r'\{\s*"alias":\s*"([^"]+)"', response.text)
        nomes = re.findall(r'"name":\s*"([^"]+)"\s*\}', response.text)
        return sorted(list(set(aliases + nomes)))
    except Exception as e:
        print(f"Falha ao obter lista: {e}")
        return []


# --- PASSO 2: CRIAR ARQUIVO DE TESTE ---
data = {'coluna': ['maçã', 'coração', 'pêssego']}
df = pd.DataFrame(data)
encoding_de_teste = 'windows-1252'
caminho_arquivo = 'test.csv'
df.to_csv(caminho_arquivo, index=False, encoding=encoding_de_teste)

# --- PASSO 3: PREPARAR DUCKDB ---
con = duckdb.connect(database=':memory:')
con.execute("INSTALL icu;")
con.execute("LOAD icu;")

# --- PASSO 4: EXECUTAR OS TESTES ---
encodings_suportados = []
encodings_falhos = []

lista_encodings = obter_lista_de_aliases_icu()
if not lista_encodings:
    print("Não foi possível obter a lista de encodings. Abortando.")
else:
    print(f"\n--- INICIANDO TESTE COM {len(lista_encodings)} ENCODINGS ---")
    for encoding_name in lista_encodings:
        try:
            # Tenta ler o CSV usando o encoding da vez
            query = f"SELECT * FROM read_csv('{caminho_arquivo}', encoding='{encoding_name}')"
            result = con.execute(query).fetchall()

            # Verificação extra: o resultado faz sentido?
            if 'maçã' in result[0][0]:
                print(f"✅ SUCESSO: '{encoding_name}'")
                encodings_suportados.append(encoding_name)
            else:
                # Ocorreu quando o encoding não deu erro, mas decodificou errado.
                print(f"⚠️ ATENÇÃO: '{encoding_name}' não deu erro, mas o resultado é inválido.")
                encodings_falhos.append(encoding_name)

        except Exception as e:
            # Se o DuckDB lançar uma exceção, o encoding é inválido.
            print(f"❌ FALHA: '{encoding_name}'")
            encodings_falhos.append(encoding_name)

    print("\n--- RESULTADO FINAL ---")
    print(f"\n✅ Encodings Suportados com Sucesso ({len(encodings_suportados)}):")
    print(encodings_suportados)

    print(f"\n❌ Encodings que Falharam ou retornaram dados incorretos ({len(encodings_falhos)}):")
    print(encodings_falhos)

# Limpa o arquivo de teste
os.remove(caminho_arquivo)