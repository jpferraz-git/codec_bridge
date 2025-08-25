import datetime
import os.path
import time
import timeit

file_100mb = "sptech100mb.txt"
file_1gb = "sptech1gb.txt"

def createCsv(path, matriz):
    with open(path, 'wb') as file:
        while os.path.getsize(path) < 1_073_741:
            for line in matriz:
                file.write(",".join(line[0]))
                file.flush()
                os.fsync(file.fileno())

def createFile100MB(text):
    with open(file_100mb, 'w') as file:
        while os.path.getsize(file_100mb) < 1_000_000:
            file.write(text * 1024)
            file.flush()
            os.fsync(file.fileno())

def createFile1Gb(text):
    with open(file_1gb, 'w') as file:
        while os.path.getsize(file_1gb) < 1_073_741_824:
            file.write(text * 1024 * 1024)
            file.flush()
            os.fsync(file.fileno())

def reader(f):
    start_time = time.perf_counter()

    with open(f, 'r') as file:
        file.read()
    end_time = time.perf_counter()
    time_runned = end_time - start_time
    print(f"Processing Time: {time_runned:.4f}")

if __name__ == '__main__':

    matriz = [["quando"], ["Previdencia"], ["12323123"], ["eles se chaamvam tenryubitoos"], ["$@#%@#@!"],
              ["porque fez isso comigo?"]]

    # reader(file_100mb)
    # reader(file_1gb)
    createCsv("repository/teste.csv", matriz)
    # createFile100MB("E quando eu sair daqui. SAIBAM QUE EU VOU, MATAR TODOS VOCÊS")
    # createFile1Gb("Sptech irada - ")
