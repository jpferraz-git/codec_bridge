import datetime
import os.path
import time
import timeit
from asyncio import timeout
from turtledemo.forest import start

# Download latest version


file_100mb = "sptech100mb.txt"
file_1gb = "sptech1gb.txt"
# print(file_size)

matriz = [["quando"],["Previdencia"],[12323123], ["eles se chaamvam tenryubitoos"], ["$@#%@#@!"], ["porque fez isso comigo?"]]
path_matriz = "aaa.csv"
def createCsv(values):
    with open(path_matriz, 'w') as file:
        while os.path.getsize(path_matriz) < 1_073_741_824:
            for line in matriz:
                file.write(line[0])
                file.flush()
                os.fsync(file.fileno())
createCsv(matriz)

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

createFile100MB("E quando eu sair daqui. SAIBAM QUE EU VOU, MATAR TODOS VOCÊS")
# createFile1Gb("Sptech irada - ")


def reader(f):
    start_time = time.perf_counter()

    with open(f, 'r') as file:
        file.read()
    end_time = time.perf_counter()
    time_runned = end_time - start_time
    print(f"Processing Time: {time_runned:.4f}")

reader(file_100mb)
reader(file_1gb)