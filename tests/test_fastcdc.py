from io import BytesIO
from mmap import mmap, ACCESS_READ
import pytest
from fastcdc.lib import *


def test_logarithm2():
    assert logarithm2(65537) == 16
    assert logarithm2(65536) == 16
    assert logarithm2(65535) == 16
    assert logarithm2(32769) == 15
    assert logarithm2(32768) == 15
    assert logarithm2(32767) == 15


def test_ceil_div():
    assert ceil_div(10, 5) == 2
    assert ceil_div(11, 5) == 3
    assert ceil_div(10, 3) == 4
    assert ceil_div(9, 3) == 3
    assert ceil_div(6, 2) == 3
    assert ceil_div(5, 2) == 3


def test_center_size():
    assert center_size(50, 100, 50) == 0
    assert center_size(200, 100, 50) == 50
    assert center_size(200, 100, 40) == 40


def test_mask_low():
    with pytest.raises(AssertionError):
        mask(0)


def test_mask():
    assert mask(24) == 16_777_215
    assert mask(16) == 65535
    assert mask(10) == 1023
    assert mask(8) == 255


def test_minimum_too_low():
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        FastCDC.new(array_, 63, 256, 1024)


def test_minimum_too_high():
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        FastCDC.new(array_, 67_108_867, 256, 1024)


def test_average_too_low():
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        FastCDC.new(array_, 64, 255, 1024)


def test_average_too_high():
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        FastCDC.new(array_, 64, 268_435_457, 1024)


def test_maximum_too_low():
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        FastCDC.new(array_, 64, 256, 1023)


def test_maximum_too_high():
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        FastCDC.new(array_, 64, 256, 1_073_741_825)


def test_all_zeros():
    array_ = bytearray([0] * 10240)
    chunker = FastCDC.new(array_, 64, 256, 1024)
    results = [c for c in chunker]
    assert len(results) == 10
    for entry in results:
        assert entry.offset % 1024 == 0
        assert entry.length == 1024


def test_sekien_16k_chunks():
    with open("SekienAkashita.jpg", "rb") as f:
        mm = mmap(f.fileno(), 0, access=ACCESS_READ)
        chunker = FastCDC.new(mm, 8192, 16384, 32768)
        results = [c for c in chunker]
        mm.close()
    assert len(results) == 6
    assert results[0].offset == 0
    assert results[0].length == 22366
    assert results[1].offset == 22366
    assert results[1].length == 8282
    assert results[2].offset == 30648
    assert results[2].length == 16303
    assert results[3].offset == 46951
    assert results[3].length == 18696
    assert results[4].offset == 65647
    assert results[4].length == 32768
    assert results[5].offset == 98415
    assert results[5].length == 11051


def test_sekien_32k_chunks():
    chunker = FastCDC.new("SekienAkashita.jpg", 16384, 32768, 65536)
    results = [c for c in chunker]
    assert len(results) == 3
    assert results[0].offset == 0
    assert results[0].length == 32857
    assert results[1].offset == 32857
    assert results[1].length == 16408
    assert results[2].offset == 49265
    assert results[2].length == 60201


def test_sekien_64k_chunks():
    with open("SekienAkashita.jpg", "rb") as f:
        mm = mmap(f.fileno(), 0, access=ACCESS_READ)
        chunker = FastCDC.new(mm, 32768, 65536, 131_072)
        results = [c for c in chunker]
        mm.close()
    assert len(results) == 2
    assert results[0].offset == 0
    assert results[0].length == 32857
    assert results[1].offset == 32857
    assert results[1].length == 76609


def test_sekien_64k_chunks_bytes():
    with open("SekienAkashita.jpg", "rb") as f:
        data = f.read()
    chunker = FastCDC.new(data, 32768, 65536, 131_072)
    results = [c for c in chunker]
    assert len(results) == 2
    assert results[0].offset == 0
    assert results[0].length == 32857
    assert results[1].offset == 32857
    assert results[1].length == 76609


def test_sekien_64k_chunks_bytearray():
    with open("SekienAkashita.jpg", "rb") as f:
        data = bytearray(f.read())
    chunker = FastCDC.new(data, 32768, 65536, 131_072)
    results = [c for c in chunker]
    assert len(results) == 2
    assert results[0].offset == 0
    assert results[0].length == 32857
    assert results[1].offset == 32857
    assert results[1].length == 76609


def test_sekien_64k_chunks_filepath():
    chunker = FastCDC.new("SekienAkashita.jpg", 32768, 65536, 131_072)
    results = [c for c in chunker]
    assert len(results) == 2
    assert results[0].offset == 0
    assert results[0].length == 32857
    assert results[1].offset == 32857
    assert results[1].length == 76609
