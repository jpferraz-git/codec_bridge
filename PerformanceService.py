import os
import psutil
import time

from pip._internal import cache


def memoria_atual():
    processo = psutil.Process(os.getpid())
    return processo.memory_info().rss / (1024 * 1024)  # MB

def gerar_csv(path, tamanho_mb, num_colunas=50):

    tamanho_alvo = tamanho_mb * 1024 * 1024

    header = ",".join([f"col{i+1}" for i in range(num_colunas)]) + "\n"

    valor_linha = ",".join([f"valor{i+1}" for i in range(num_colunas)]) + "\n"

    inicio = time.perf_counter()

    memoria_inicial = memoria_atual()

    with open(path, "w", encoding="big5") as file:
        file.write(header)

        while os.path.getsize(path) < tamanho_alvo:
            file.write(valor_linha)

    fim = time.perf_counter()
    memoria_final = memoria_atual()

    print(f"Tempo: {fim - inicio:.2f} segundos")
    print(f"Memória usada: {memoria_final - memoria_inicial:.2f} MB")

    print(f"✅ Arquivo {path} gerado com ~{tamanho_mb}MB, {num_colunas} colunas.")


def benchmark_streaming(path):
    processo = psutil.Process(os.getpid())

    inicio = time.perf_counter()
    memoria_inicial = processo.memory_info().rss / (1024*1024)

    linhas = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linhas += 1

    fim = time.perf_counter()

    memoria_final = processo.memory_info().rss / (1024*1024)

    print(f"Arquivo: {path}")
    print(f"Linhas lidas: {linhas}")
    print(f"Tempo: {fim - inicio:.2f} segundos")
    print(f"Memória usada: {memoria_final - memoria_inicial:.2f} MB")
    print("-" * 40)

def write_file_in_chunks(path, chunks_size = 1024):
    with open(path, 'wb') as file:
        while chunk := file.read(chunks_size):
            yield chunk


def write_csv_in_chunks(file_path, matriz, file_size, chunk_size = 1024):

    file_size_in_mb = file_size * 1024 * 1024
    with open(file_path, 'w') as file:
        memoria_inicial = memoria_atual()
        inicio = time.perf_counter()
        while os.path.getsize(file_path) < file_size_in_mb:
            for i in range(0, len(matriz), chunk_size):
                chunk = matriz[i:i + chunk_size]
                for linha in chunk:
                    linha_csv = ",".join(map(str, linha))
                    file.write(linha_csv + "\n")

    fim = time.perf_counter()
    memoria_final = memoria_atual()
    print(f"TEMPO TOTAL = {fim - inicio}")
    print(f"MEMÓRIA GASTA = {memoria_final - memoria_inicial:2.f}")

if __name__ == "__main__":

    gerar_csv("repository/ISO.csv", 100)

    # write_csv_in_chunks("testes_performance/100mbChunk.csv",
    # matriz=([["pinto", "alavanca"],
    #         ["saco", "marreta"]
    #         ]),
    # file_size=100,
    # chunk_size=1024)

    # benchmark_streaming("testes_performance/10gb.csv")