from typing import Iterable, Iterator, Generator

def generator(range):
    while True:
        yield range

g = generator([1,2,3])

nums_gen = (i for i in range(10_000_000))
for x in nums_gen: print(x)
