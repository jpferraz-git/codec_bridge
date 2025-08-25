# fast_detector.py
import chardet


def detect_fast(filepath: str, sample_size_bytes: int = 10 * 1024 * 1024) -> str | None:
    """
    Lê apenas os primeiros 'sample_size_bytes' de um arquivo para detectar
    o encoding de forma rápida.
    """
    try:
        with open(filepath, 'rb') as f:
            sample = f.read(sample_size_bytes)
            if not sample:
                return None  # Arquivo vazio

            result = chardet.detect(sample)
            return result['encoding']
    except FileNotFoundError:
        print("Arquivo não encontrado")
        return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

# Teste rápido (precisa de um arquivo para testar)
# encoding_base = detect_fast('meu_arquivo_gigante.csv')
# print(f"Encoding base detectado: {encoding_base}")

