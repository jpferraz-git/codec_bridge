import csv
import os

# Diretório onde os arquivos serão salvos
output_dir = "csv_encodings"
os.makedirs(output_dir, exist_ok=True)

# Lista de encodings que queremos testar
encodings = [
    "utf-8", "utf-16", "iso-8859-1", "windows-1252",
    "ascii", "iso-8859-2", "iso-8859-5", "koi8-r",
    "shift_jis", "gbk", "big5", "windows-1253", "iso-8859-15"
]

# DICIONÁRIO DE CARACTERES ESPECIAIS
# A chave é o encoding, o valor é um caractere que o torna único.
# Isso força o arquivo a NÃO ser detectado como ASCII.
killer_chars = {
    "iso-8859-1": "ç",  # Caractere latino comum
    "windows-1252": "€",  # Símbolo do Euro, existe no win-1252 mas não no iso-8859-1
    "iso-8859-2": "ść",  # Caracteres do Leste Europeu
    "iso-8859-5": "ДЖ",  # Caracteres Cirílicos
    "koi8-r": "ДЖ",  # Caracteres Cirílicos
    "shift_jis": "ア",  # Katakana Japonês
    "gbk": "你好",  # Chinês
    "big5": "你好",  # Chinês Tradicional
    "windows-1253": "αβ",  # Grego
    "iso-8859-15": "€",  # Símbolo do Euro
    # UTF-8 e UTF-16 podem conter qualquer coisa, vamos usar um emoji
    "utf-8": "🚀",
    "utf-16": "🚀",
}


# Gerar conteúdo fictício: 10 linhas x 5 colunas
def gerar_rows(char_exemplo=""):
    # Adiciona o caractere especial na primeira célula de cada linha
    return [[f"Dado_{i}_{j}{char_exemplo if j == 0 else ''}" for j in range(5)] for i in range(10)]


# Gerar os arquivos CSV
for enc in encodings:
    filename = os.path.join(output_dir, f"exemplo_{enc}.csv")

    # Pega o caractere especial para o encoding atual
    char_especial = killer_chars.get(enc, "")
    rows = gerar_rows(char_especial)

    try:
        with open(filename, mode="w", encoding=enc, newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Coluna_1", "Coluna_2", "Coluna_3", "Coluna_4", "Coluna_5"])
            writer.writerows(rows)
        print(f"✅ Gerado: {filename} (com char: '{char_especial}')")
    except UnicodeEncodeError:
        print(f"❌ Erro de encode com {enc}: O caractere '{char_especial}' não existe neste encoding.")
    except Exception as e:
        print(f"⚠️ Erro inesperado com encoding {enc}: {e}")
