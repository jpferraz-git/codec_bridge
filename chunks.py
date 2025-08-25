import datetime
import time


print(time.process_time())
chunk = 512

sentence = [
    ["Gozaram na minha cara pessoal\n" * 1_000_000],
    ["Gozaram na minha cara pessoal" * 1_000_000]
            ]
f = "chunk.txt"

print(f"start_time = ", datetime.datetime.now())

def fileWriter(f):
    with open(f, 'w', buffering=512) as file:
        for item in sentence:
            for a in item:
                file.write(a)

def fileReader(f):
    with open(f, 'r', buffering=512) as file:
        file.read()

fileReader(f)

print(f"finish_time = ", datetime.datetime.now() )