from typing import Iterable

def chain(iterable: Iterable):
    for item in iterable:
        yield from item