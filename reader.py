import random
import operator

text = "O rato roeu a roupa do rei de roma"
f = "file.txt"


def convertCodePoint(text):
    encoding = text.encode('utf-8')
    code_point = [format(c, '08b') for c in encoding]
    append = [f"b'{c}'" for c in code_point]
    print(code_point)
    return append

convertCodePoint(text)

def writeFile(text):
    enconding = text.encode('utf-8')
    with open(f, 'wb') as file:
        file.write(enconding)


writeFile(text)

def readFile(f):
    with open(f, 'rb') as file:
        print(file.read())

readFile(f)

# def random_bytes(size):
#     bytes = []
#     for x in range(size):
#         bytes.append(random.randrange(0,255))
#
#     return bytes
#
# def displayBytes(bytes):
#     print("-"*20)
#     for index, item in enumerate(bytes, start=1):
#         print(f'{index} = {item} ({hex(item)})')
#
#     print("-" * 20)
#
# #Write Bytes
# def writeBytes(filename, bytes):
#     with open(filename, 'wb') as file:
#         for b in bytes:
#             file.write(b.to_bytes(1, byteorder='big'))
#
# #Read BYtes
#
# def readBytes(filename):
#     bytes = []
#     with open(filename, 'rb') as file:
#         while True:
#             b = file.read(1)
#             if not b:
#                 break
#             bytes.append(int.from_bytes(b, byteorder='big'))
#     return bytes
#
# outbytes = random_bytes(10)
# displayBytes(outbytes)
#
# filepath = 'test.txt'
# writeBytes(filepath, outbytes)
#
# inbytes = readBytes(filepath)
# displayBytes(inbytes)
#
# print(f'Match: {operator.eq(outbytes, inbytes)}')
