# A biblioteca do estagiário não reimplementa a detecção. Ela a USA!
from charset_normalizer import from_bytes

# Esta é a parte que SÓ a biblioteca dele tem.
# from .translator import get_alias


def detect_for_pipeline(filepath: str, target: str, sample_mb: int = 10):
    """
    Esta função é o coração da biblioteca dele.
    Simples, focada e resolve um problema real.
    """
    # 1. Ganho de Performance: lê só o começo do arquivo.
    with open(filepath, 'rb') as f:
        sample = f.read(sample_mb * 1024 * 1024)

    # 2. Delega a detecção complexa para uma biblioteca especialista.
    matches = from_bytes(sample)
    best_match = matches.best()

    if not best_match:
        return None

    base_encoding = best_match.encoding

    # 3. Aplica a sua funcionalidade única e de grande valor.
    final_encoding_alias = get_alias(base_encoding, target)

    return final_encoding_alias


# minha_biblioteca.py
# from .encoding_translator import get_alias
# from .fast_detector import detect_fast

# def detect(filepath: str, target: str = 'python', sample_mb: int = 10) -> str | None:
#     """
#     Função principal da biblioteca. Detecta rapidamente o encoding de um arquivo
#     e já retorna o nome formatado para o sistema de destino.
#
#     :param filepath: Caminho para o arquivo.
#     :param target: O sistema de destino ('python', 'spark', 'duckdb', etc.).
#     :param sample_mb: Quantos megabytes do início do arquivo ler.
#     """
#     sample_size_bytes = sample_mb * 1024 * 1024
#
#     # Passo 1: Usar o detector rápido para pegar o encoding base
#     base_encoding = detect_fast(filepath, sample_size_bytes)
#
#     if not base_encoding:
#         return None
#
#     # Passo 2: Usar o tradutor para obter o alias correto
#     final_encoding = get_alias(base_encoding, target)
#
#     # Se não houver um alias específico, retornar o encoding base como fallback
#     return final_encoding if final_encoding else base_encoding
#
# # Exemplo de uso final
# # encoding_para_spark = detect('meu_arquivo_gigante.csv', target='spark')
# # if encoding_para_spark:
# #     df = spark.read.csv('meu_arquivo_gigante.csv', encoding=encoding_para_spark)