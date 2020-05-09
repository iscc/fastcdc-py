# -*- coding: utf-8 -*-
"""
True to the original port of https://github.com/nlfiedler/fastcdc-rs
"""
import math
import os
from dataclasses import dataclass
from mmap import mmap, ACCESS_READ
from typing import Optional, ByteString, BinaryIO, Text, Union
from fastcdc.const import (
    TABLE,
    MINIMUM_MIN,
    MINIMUM_MAX,
    AVERAGE_MIN,
    AVERAGE_MAX,
    MAXIMUM_MIN,
    MAXIMUM_MAX,
)


@dataclass
class Chunk:
    offset: int
    length: int


@dataclass
class FastCDC:

    source: Union[ByteString, BinaryIO, Text]
    bytes_processed: int
    bytes_remaining: int
    min_size: int
    avg_size: int
    max_size: int
    mask_s: int
    mask_l: int

    @classmethod
    def new(
        cls,
        source: Union[ByteString, BinaryIO, Text],
        min_size: int,
        avg_size: int,
        max_size: int,
    ):
        assert min_size >= MINIMUM_MIN
        assert min_size <= MINIMUM_MAX
        assert avg_size >= AVERAGE_MIN
        assert avg_size <= AVERAGE_MAX
        assert max_size >= MAXIMUM_MIN
        assert max_size <= MAXIMUM_MAX
        bits = logarithm2(avg_size)
        mask_s = mask(bits + 1)
        mask_l = mask(bits - 1)
        if isinstance(source, BinaryIO):
            source = mmap(source.fileno(), 0, access=ACCESS_READ)
            source.seek(0)
        if isinstance(source, Text):
            infile = os.open(source, os.O_RDONLY)
            source = mmap(infile, 0, access=ACCESS_READ)
        return cls(source, 0, len(source), min_size, avg_size, max_size, mask_s, mask_l)

    def cut(self, source_offset: int, source_size: int) -> int:
        if source_size <= self.min_size:
            return source_size
        else:
            if source_size > self.max_size:
                source_size = self.max_size
            source_start = source_offset
            source_len1 = source_offset + center_size(
                self.avg_size, self.min_size, source_size
            )
            source_len2 = source_offset + source_size
            hash_ = 0
            source_offset += self.min_size
            while source_offset < source_len1:
                index = self.source[source_offset]
                source_offset += 1
                hash_ = (hash_ >> 1) + TABLE[index]
                if hash_ & self.mask_s == 0:
                    return source_offset - source_start

            while source_offset < source_len2:
                index = self.source[source_offset]
                source_offset += 1
                hash_ = (hash_ >> 1) + TABLE[index]
                if hash_ & self.mask_l == 0:
                    return source_offset - source_start
            return source_size

    def __iter__(self):
        self.bytes_processed = 0
        self.bytes_remaining = len(self.source)
        return self

    def __next__(self) -> Optional[Chunk]:
        if self.bytes_remaining == 0:
            raise StopIteration
        else:
            chunk_size = self.cut(self.bytes_processed, self.bytes_remaining)
            chunk_start = self.bytes_processed
            self.bytes_processed += chunk_size
            self.bytes_remaining -= chunk_size
            return Chunk(offset=chunk_start, length=chunk_size)

    def __del__(self):
        if hasattr(self.source, "close"):
            self.source.close()


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
