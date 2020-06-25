import pytest
from fastcdc.original import *
from fastcdc.fastcdc_py import fastcdc_py
from fastcdc.fastcdc_cy import fastcdc_cy
from tests import TEST_FILE


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_minimum_too_low(chunk_func):
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        chunk_func(array_, 63, 256, 1024)


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_minimum_too_high(chunk_func):
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        chunk_func(array_, 67_108_867, 256, 1024)


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_average_too_low(chunk_func):
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        chunk_func(array_, 64, 255, 1024)


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_average_too_high(chunk_func):
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        chunk_func(array_, 64, 268_435_457, 1024)


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_maximum_too_low(chunk_func):
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        chunk_func(array_, 64, 256, 1023)


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_maximum_too_high_a(chunk_func):
    array_ = bytearray([0] * 2048)
    with pytest.raises(AssertionError):
        chunk_func(array_, 64, 256, 1_073_741_825)


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_all_zeros(chunk_func, benchmark):
    array_ = bytearray([0] * 10240)

    @benchmark
    def make_chunks():
        chunker = chunk_func(array_, 64, 256, 1024)
        results = [c for c in chunker]
        assert len(results) == 10
        for entry in results:
            assert entry.offset % 1024 == 0
            assert entry.length == 1024


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_sekien_16k_chunks(chunk_func, benchmark):
    @benchmark
    def make_chunks():
        chunker = chunk_func(TEST_FILE, 8192, 16384, 32768)
        results = [c for c in chunker]
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


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_sekien_32k_chunks(chunk_func, benchmark):
    @benchmark
    def make_chunks():
        chunker = chunk_func(TEST_FILE, 16384, 32768, 65536)
        results = [c for c in chunker]
        assert len(results) == 3
        assert results[0].offset == 0
        assert results[0].length == 32857
        assert results[1].offset == 32857
        assert results[1].length == 16408
        assert results[2].offset == 49265
        assert results[2].length == 60201


@pytest.mark.parametrize("chunk_func", [FastCDC.new, fastcdc_py, fastcdc_cy])
def test_sekien_64k_chunks(chunk_func, benchmark):
    @benchmark
    def make_chunks():
        chunker = chunk_func(TEST_FILE, 32768, 65536, 131072)
        results = [c for c in chunker]
        assert len(results) == 2
        assert results[0].offset == 0
        assert results[0].length == 32857
        assert results[1].offset == 32857
        assert results[1].length == 76609
