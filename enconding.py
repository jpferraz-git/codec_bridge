string = "abacaxi"
emoji = "📦"
# print(ord(string)) #Apenas para Car

bytes = emoji.encode("utf8")
print(bytes)
lista = [format(b, '08b') for b in bytes]

print(lista)
