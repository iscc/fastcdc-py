# -*- coding: utf-8 -*-
from libc.stdint cimport uint32_t
from libc.math cimport log2, lround


cpdef uint32_t logarithm2(uint32_t value):
    return lround(log2(value))


cpdef uint32_t ceil_div(uint32_t x, uint32_t y):
    return (x + y - 1) // y


cpdef uint32_t center_size(uint32_t average, uint32_t minimum, uint32_t source_size):
    cdef uint32_t offset = minimum + ceil_div(minimum, 2)
    if offset > average:
        offset = average
    cdef uint32_t size = average - offset
    if size > source_size:
        return source_size
    return size


cpdef uint32_t mask(uint32_t bits):
    return 2 ** bits - 1
