# -*- coding: utf-8 -*-
import pytest
from fastcdc import utils


def test_logarithm2():
    assert utils.logarithm2(65537) == 16
    assert utils.logarithm2(65536) == 16
    assert utils.logarithm2(65535) == 16
    assert utils.logarithm2(32769) == 15
    assert utils.logarithm2(32768) == 15
    assert utils.logarithm2(32767) == 15


def test_ceil_div():
    assert utils.ceil_div(10, 5) == 2
    assert utils.ceil_div(11, 5) == 3
    assert utils.ceil_div(10, 3) == 4
    assert utils.ceil_div(9, 3) == 3
    assert utils.ceil_div(6, 2) == 3
    assert utils.ceil_div(5, 2) == 3


def test_center_size():
    assert utils.center_size(50, 100, 50) == 0
    assert utils.center_size(200, 100, 50) == 50
    assert utils.center_size(200, 100, 40) == 40


def test_mask():
    assert utils.mask(24) == 16_777_215
    assert utils.mask(16) == 65535
    assert utils.mask(10) == 1023
    assert utils.mask(8) == 255


def test_mask_low():
    with pytest.raises(AssertionError):
        utils.mask(0)
