# -*- coding: utf-8 -*-
import math


def center_size(average: int, minimum: int, source_size: int) -> int:
    offset = minimum + ceil_div(minimum, 2)
    if offset > average:
        offset = average
    size = average - offset
    if size > source_size:
        return source_size
    else:
        return size


def ceil_div(x, y):
    return (x + y - 1) // y


def logarithm2(value: int) -> int:
    return round(math.log(value, 2))


def mask(bits: int) -> int:
    assert bits >= 1
    assert bits <= 31
    return 2 ** bits - 1
