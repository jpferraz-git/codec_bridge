import datetime

chunk = 512

sentence = [
    ["Gozaram na minha cara pessoal\n" * 1_000_000],
    ["Gozaram na minha cara pessoal" * 1_000_000]
            ]
f = "chunk.txt"

print(f"start_time = ", datetime.datetime.now())

def fileWriter(f):
    with open(f, 'w', chunk) as file:
        for item in sentence:
            for a in item:
                file.write(a)

def fileReader(f):
    with open(f, 'r', chunk) as file:
        print(file.read())

fileReader(f)

print(f"finish_time = ", datetime.datetime.now() )