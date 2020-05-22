# -*- coding: utf-8 -*-
import pytest
from fastcdc import utils
import pyximport

pyximport.install()
from fastcdc import cylib


@pytest.mark.parametrize("module", [utils, cylib])
def test_logarithm2(module, benchmark):
    assert benchmark(module.logarithm2, 65537) == 16
    assert module.logarithm2(65536) == 16
    assert module.logarithm2(65535) == 16
    assert module.logarithm2(32769) == 15
    assert module.logarithm2(32768) == 15
    assert module.logarithm2(32767) == 15


@pytest.mark.parametrize("module", [utils, cylib])
def test_ceil_div(module, benchmark):
    assert benchmark(module.ceil_div, 10, 5) == 2
    assert module.ceil_div(11, 5) == 3
    assert module.ceil_div(10, 3) == 4
    assert module.ceil_div(9, 3) == 3
    assert module.ceil_div(6, 2) == 3
    assert module.ceil_div(5, 2) == 3


@pytest.mark.parametrize("module", [utils, cylib])
def test_center_size(module, benchmark):
    assert benchmark(module.center_size, 50, 100, 50) == 0
    assert module.center_size(200, 100, 50) == 50
    assert module.center_size(200, 100, 40) == 40


@pytest.mark.parametrize("module", [utils, cylib])
def test_mask(module, benchmark):
    assert benchmark(module.mask, 24) == 16_777_215
    assert module.mask(16) == 65535
    assert module.mask(10) == 1023
    assert module.mask(8) == 255


def test_mask_low():
    with pytest.raises(AssertionError):
        utils.mask(0)
