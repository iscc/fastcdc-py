# -*- coding: utf-8 -*-
"""
Rewrite of original as generator function with convenient highler level API.

- accept streams or filenames as input (you don´t have to read the entire stream)
- optionally calculate chunk hashes and also yield raw chunk data
- provide custom hash function
"""
from dataclasses import dataclass
import math
from io import BytesIO
from typing import Generator, Optional, Callable, Union, ByteString, BinaryIO, Text
import fastcdc.const
from fastcdc import original


@dataclass
class Chunk:
    """Represents a (variable sized) chunk of a file."""

    offset: int
    length: int
    data: bytes = b""
    hash: str = ""


def chunkify(
    data: Union[BytesIO, ByteString, BinaryIO, Text],
    min_size: Optional[int] = None,
    avg_size: Optional[int] = 8192,
    max_size: Optional[int] = None,
    fat: Optional[bool] = False,
    hf: Optional[Callable] = None,
) -> Generator:
    """Returns a generator that yields Chunk objects.
    :param data: A readable stream or a file path (str).
    :param min_size: Minumum chunk size (defaults to avg_size // 4).
    :param avg_size: Targeted average chunk size (default 8192 bytes).
    :param max_size: Maximum chunk size (defaults to avg_size * 8).
    :param fat: Add chunk bytes to Chunk.data (default=False).
    :param hf: Use custom hash function (defaults to sha256).
    """

    if min_size is None:
        min_size = avg_size // 4
    if max_size is None:
        max_size = avg_size * 8

    assert fastcdc.const.MINIMUM_MIN <= min_size <= fastcdc.const.MINIMUM_MAX
    assert fastcdc.const.AVERAGE_MIN <= avg_size <= fastcdc.const.AVERAGE_MAX
    assert fastcdc.const.MAXIMUM_MIN <= max_size <= fastcdc.const.MAXIMUM_MAX

    # Ensure we have a readable stream
    if isinstance(data, str):
        data = open(data, "rb")
    elif not hasattr(data, "read"):
        data = BytesIO(data)
    return chunk_gen(data, min_size, avg_size, max_size, fat, hf)


def chunk_gen(data, min_size, avg_size, max_size, fat, hf):
    for chunk in chunker(data, min_size, avg_size, max_size):
        if hf is not None:
            chunk.hash = hf(chunk.data).hexdigest()
        if fat is not False:
            chunk.data = b""
        yield chunk


def chunker(data: BytesIO, min_size: int, avg_size: int, max_size: int) -> Generator:

    bits = round(math.log(avg_size, 2))
    mask_s = 2 ** (bits + 1) - 1
    mask_l = 2 ** (bits - 1) - 1

    section = data.read(max_size)
    offset = 0
    boundary = 0
    while True:

        if len(section) < max_size:
            section += data.read(max_size)
        if len(section) == 0:
            break
        data_length = len(section)
        i = min_size
        pattern = 0

        if data_length <= min_size:
            boundary = data_length
            break

        barrier = original.center_size(avg_size, min_size, data_length)
        while i < barrier:
            pattern = (pattern >> 1) + fastcdc.const.TABLE[section[i]]
            if not pattern & mask_s:
                boundary = i + 1
                break
            i += 1

        barrier = min(max_size, data_length)
        while i < barrier:
            pattern = (pattern >> 1) + fastcdc.const.TABLE[section[i]]
            if not pattern & mask_l:
                boundary = i + 1
                break
            i += 1
        else:
            boundary = i

        yield Chunk(offset=offset, length=boundary, data=section[:boundary])
        section = section[boundary:]
        offset += boundary
