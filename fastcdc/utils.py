# -*- coding: utf-8 -*-
import math
import mmap
from io import BufferedReader
from os import scandir
from pathlib import Path
from typing import List
import hashlib
import click
from typing import Union


Data = Union[str, Path, BufferedReader, bytes, bytearray, mmap.mmap, memoryview]


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
    return 2**bits - 1


class DefaultHelp(click.Command):
    def __init__(self, *args, **kwargs):
        context_settings = kwargs.setdefault("context_settings", {})
        if "help_option_names" not in context_settings:
            context_settings["help_option_names"] = ["-h", "--help"]
        self.help_flag = context_settings["help_option_names"][0]
        super(DefaultHelp, self).__init__(*args, **kwargs)

    def parse_args(self, ctx, args):
        if not args:
            args = [self.help_flag]
        return super(DefaultHelp, self).parse_args(ctx, args)


def supported_hashes() -> List[str]:
    supported = list(hashlib.algorithms_guaranteed)
    try:
        import xxhash

        supported.extend(["xxh32", "xxh64"])
        hashlib.xxh32 = xxhash.xxh32
        hashlib.xxh64 = xxhash.xxh64
    except ImportError:
        pass
    try:
        import blake3

        supported.append("blake3")
        hashlib.blake3 = blake3.blake3
    except ImportError:
        pass
    return supported


def iter_files(path, recursive=False):
    try:
        if recursive:
            for entry in scandir(path):
                if entry.is_dir(follow_symlinks=False):
                    yield from iter_files(entry.path, recursive)
                elif not entry.is_symlink():
                    yield entry
        else:
            for entry in scandir(path):
                if entry.is_file() and not entry.is_symlink():
                    yield entry
    except PermissionError:
        click.echo("\nPermissionError for {}".format(path))


def get_memoryview(data):
    # Handle file path string and Path object
    if isinstance(data, (str, Path)):
        with open(data, "rb") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            return memoryview(mm)

    # Handle file object opened in 'rb' mode
    if hasattr(data, "fileno"):
        mm = mmap.mmap(data.fileno(), 0, access=mmap.ACCESS_READ)
        return memoryview(mm)

    # Handle BufferedReader
    if isinstance(data, BufferedReader):
        mm = mmap.mmap(data.raw.fileno(), 0, access=mmap.ACCESS_READ)
        return memoryview(mm)

    # Handle bytes, bytearray, mmap.mmap, and memoryview objects
    if isinstance(data, (bytes, bytearray, mmap.mmap, memoryview)):
        return memoryview(data)

    raise TypeError("Unsupported data type")
