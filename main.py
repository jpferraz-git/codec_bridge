import unicodedata

h_muito_foda = "\u210B\u0327"
print(unicodedata.normalize("NFKD", h_muito_foda))

h_irado = "H\u0327"
print(unicodedata.normalize("NFKD", h_irado))

