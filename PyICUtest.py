import datetime
import json
import os.path

import chardet
import charset_normalizer


# String with unknown encoding
path = "sptech1gb.txt"

# Detect the encoding
with open(path, "rb") as file:
    buffer = file.read(10)
    result = chardet.detect(buffer)["encoding"]
    print(result)

with open(path, "rb") as file:
    buffer = file.read(10000_00)
    result = charset_normalizer.detect(buffer)["encoding"]
    print(result)

def json_writer():
    path = "json.json"
    data = {
        "caralhos": "durus"
    },
    with open(path, "w") as file:
        while os.path.getsize(path) < 100_000 * 1024:
            json.dump(data, file, indent=4)

json_writer()