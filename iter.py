from typing import Iterable, Iterator, Generator
#Iterable é o Objeto que pode ser iterado, ou seja, passsar pelo Iterator
#Também tem o Generator, que gera um objeto Iterable que pode serr Iterado
def generator(range):
    while True:
        yield range

g = generator([1,2,3])

nums_gen = (i for i in range(1000))
for x in nums_gen: print(x)

def twoGenerator():
    yield 1
    yield 2
    yield 3

g = twoGenerator()
print(next(g))
print(next(g))

list = [4,5,6]

i = iter(list)

print(next(i))
print(next(i))

