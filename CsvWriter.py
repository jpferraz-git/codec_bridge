import csv
import os

# Diretório onde os arquivos serão salvos
output_dir = "csv_encodings"
os.makedirs(output_dir, exist_ok=True)

# Lista dos 20 encodings mais usados (sem duplicatas)
encodings = [
    "utf-8", "utf-16", "utf-32", "iso-8859-1", "windows-1252",
    "ascii", "iso-8859-2", "iso-8859-5", "koi8-r", "macroman",
    "shift_jis", "euc_jp", "iso2022_jp", "gb2312", "gbk",
    "big5", "iso-8859-6", "iso-8859-8", "tis-620", "iso-8859-15"
]

# Gerar conteúdo fictício: 10 linhas x 5 colunas
rows = [[f"Dado_{i}_{j}" for j in range(5)] for i in range(10)]

# Gerar os arquivos CSV
for enc in encodings:
    filename = os.path.join(output_dir, f"exemplo_{enc}.csv")
    try:
        with open(filename, mode="w", encoding=enc, newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Coluna_1", "Coluna_2", "Coluna_3", "Coluna_4", "Coluna_5"])
            writer.writerows(rows)
        print(f"✅ Gerado: {filename}")
    except Exception as e:
        print(f"⚠️ Erro com encoding {enc}: {e}")
