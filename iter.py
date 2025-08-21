from typing import Iterable, Iterator, Generator
#
# def generator(range):
#     while True:
#         yield range
#
# g = generator([1,2,3])
#
# nums_gen = (i for i in range(10_000_000))
# for x in nums_gen: print(x)

def contador():
    yield 1
    yield 2
    yield 3

g = contador()

print(iter(g))
print(iter(g))
print(next(g))