# -*- coding: utf-8 -*-
from typing import Callable, Iterator

cimport cython
from libc.stdint cimport uint32_t, uint8_t
from libc.math cimport log2, lround
from fastcdc.utils import get_memoryview, Data


def fastcdc_cy(data, min_size=None, avg_size=8192, max_size=None, fat=False, hf=None):
    # type: (Data, int|None, int, int|None, bool, Callable|None) -> Iterator["Chunk"]
    """
    Perform Fast Content-Defined Chunking (FastCDC) on input data.

    :param data: Input data to be chunked
    :param min_size: Minimum chunk size (default: avg_size // 4)
    :param avg_size: Average chunk size (default: 8192)
    :param max_size: Maximum chunk size (default: avg_size * 8)
    :param fat: If True, include chunk offset and size in output
    :param hf: Hash function to use for chunking (default: None)
    :return: Generator yielding Chunk objects
    """
    if min_size is None:
        min_size = avg_size // 4
    if max_size is None:
        max_size = avg_size * 8

    assert MINIMUM_MIN <= min_size <= MINIMUM_MAX
    assert AVERAGE_MIN <= avg_size <= AVERAGE_MAX
    assert MAXIMUM_MIN <= max_size <= MAXIMUM_MAX

    mview = get_memoryview(data)
    return chunk_generator(mview, min_size, avg_size, max_size, fat, hf)


@cython.boundscheck(False)
@cython.wraparound(False)
def chunk_generator(memview, min_size, avg_size, max_size, fat, hf):
    # type: (memoryview, int, int, int, bool, Callable) -> Iterator[Chunk]
    """
    Generate chunks from memoryview data using FastCDC algorithm.

    :param memview: Input data as a memoryview
    :param min_size: Minimum chunk size
    :param avg_size: Average chunk size
    :param max_size: Maximum chunk size
    :param fat: If True, include chunk data in output
    :param hf: Hash function to use for chunking
    :return: Generator yielding Chunk objects
    """
    cs = center_size(avg_size, min_size, max_size)
    bits = logarithm2(avg_size)
    mask_s = mask(bits + 1)
    mask_l = mask(bits - 1)
    read_size = max(1024 * 64, max_size)
    offset = 0
    while offset < len(memview):
        blob = memview[offset:offset + read_size]
        cp = cdc_offset(blob, min_size, max_size, cs, mask_s, mask_l)
        raw = bytes(blob[:cp]) if fat else b''
        h = hf(blob[:cp]).hexdigest() if hf else ''
        yield Chunk(offset, cp, raw, h)
        offset += cp


@cython.boundscheck(False)
@cython.wraparound(False)
cdef uint32_t cdc_offset(
    const uint8_t[:] data,
    uint32_t mi,
    uint32_t ma,
    uint32_t cs,
    uint32_t mask_s,
    uint32_t mask_l
):
    cdef uint32_t pattern, i, size, barrier
    pattern = 0
    size = len(data)
    i = min(mi, size)
    barrier = min(cs, size)
    while i < barrier:
        pattern = (pattern >> 1) + GEAR[data[i]]
        if not pattern & mask_s:
            return i + 1
        i += 1
    barrier = min(ma, size)
    while i < barrier:
        pattern = (pattern >> 1) + GEAR[data[i]]
        if not pattern & mask_l:
            return i + 1
        i += 1
    return i


########################################################################################
# Utility functions and classes                                                        #
########################################################################################


cdef class Chunk:
    cdef readonly unsigned long long offset
    cdef readonly int length
    cdef readonly bytes data
    cdef readonly str hash

    def __init__(self, offset, length, data, hash):
        self.offset = offset
        self.length = length
        self.data = data
        self.hash = hash

    def __str__(self):
        return "hash={} offset={} size={}".format(
            self.hash, self.offset, self.length
        )


cdef uint32_t logarithm2(uint32_t value):
    return lround(log2(value))


cdef uint32_t ceil_div(uint32_t x, uint32_t y):
    return (x + y - 1) // y


cdef uint32_t center_size(uint32_t average, uint32_t minimum, uint32_t source_size):
    cdef uint32_t offset = minimum + ceil_div(minimum, 2)
    if offset > average:
        offset = average
    cdef uint32_t size = average - offset
    if size > source_size:
        return source_size
    return size


cdef uint32_t mask(uint32_t bits):
    return 2 ** bits - 1


########################################################################################
# Constants                                                                            #
########################################################################################

# Smallest acceptable value for the minimum chunk size.
cdef MINIMUM_MIN = 64
# Largest acceptable value for the minimum chunk size.
cdef MINIMUM_MAX = 67_108_864
# Smallest acceptable value for the average chunk size.
cdef AVERAGE_MIN = 256
# Largest acceptable value for the average chunk size.
cdef AVERAGE_MAX = 268_435_456
# Smallest acceptable value for the maximum chunk size.
cdef MAXIMUM_MIN = 1024
# Largest acceptable value for the maximum chunk size.
cdef MAXIMUM_MAX = 1_073_741_824


cdef uint32_t[256]  GEAR = [
  1553318008, 574654857,  759734804,  310648967,  1393527547, 1195718329,
  694400241,  1154184075, 1319583805, 1298164590, 122602963,  989043992,
  1918895050, 933636724,  1369634190, 1963341198, 1565176104, 1296753019,
  1105746212, 1191982839, 1195494369, 29065008,   1635524067, 722221599,
  1355059059, 564669751,  1620421856, 1100048288, 1018120624, 1087284781,
  1723604070, 1415454125, 737834957,  1854265892, 1605418437, 1697446953,
  973791659,  674750707,  1669838606, 320299026,  1130545851, 1725494449,
  939321396,  748475270,  554975894,  1651665064, 1695413559, 671470969,
  992078781,  1935142196, 1062778243, 1901125066, 1935811166, 1644847216,
  744420649,  2068980838, 1988851904, 1263854878, 1979320293, 111370182,
  817303588,  478553825,  694867320,  685227566,  345022554,  2095989693,
  1770739427, 165413158,  1322704750, 46251975,   710520147,  700507188,
  2104251000, 1350123687, 1593227923, 1756802846, 1179873910, 1629210470,
  358373501,  807118919,  751426983,  172199468,  174707988,  1951167187,
  1328704411, 2129871494, 1242495143, 1793093310, 1721521010, 306195915,
  1609230749, 1992815783, 1790818204, 234528824,  551692332,  1930351755,
  110996527,  378457918,  638641695,  743517326,  368806918,  1583529078,
  1767199029, 182158924,  1114175764, 882553770,  552467890,  1366456705,
  934589400,  1574008098, 1798094820, 1548210079, 821697741,  601807702,
  332526858,  1693310695, 136360183,  1189114632, 506273277,  397438002,
  620771032,  676183860,  1747529440, 909035644,  142389739,  1991534368,
  272707803,  1905681287, 1210958911, 596176677,  1380009185, 1153270606,
  1150188963, 1067903737, 1020928348, 978324723,  962376754,  1368724127,
  1133797255, 1367747748, 1458212849, 537933020,  1295159285, 2104731913,
  1647629177, 1691336604, 922114202,  170715530,  1608833393, 62657989,
  1140989235, 381784875,  928003604,  449509021,  1057208185, 1239816707,
  525522922,  476962140,  102897870,  132620570,  419788154,  2095057491,
  1240747817, 1271689397, 973007445,  1380110056, 1021668229, 12064370,
  1186917580, 1017163094, 597085928,  2018803520, 1795688603, 1722115921,
  2015264326, 506263638,  1002517905, 1229603330, 1376031959, 763839898,
  1970623926, 1109937345, 524780807,  1976131071, 905940439,  1313298413,
  772929676,  1578848328, 1108240025, 577439381,  1293318580, 1512203375,
  371003697,  308046041,  320070446,  1252546340, 568098497,  1341794814,
  1922466690, 480833267,  1060838440, 969079660,  1836468543, 2049091118,
  2023431210, 383830867,  2112679659, 231203270,  1551220541, 1377927987,
  275637462,  2110145570, 1700335604, 738389040,  1688841319, 1506456297,
  1243730675, 258043479,  599084776,  41093802,   792486733,  1897397356,
  28077829,   1520357900, 361516586,  1119263216, 209458355,  45979201,
  363681532,  477245280,  2107748241, 601938891,  244572459,  1689418013,
  1141711990, 1485744349, 1181066840, 1950794776, 410494836,  1445347454,
  2137242950, 852679640,  1014566730, 1999335993, 1871390758, 1736439305,
  231222289,  603972436,  783045542,  370384393,  184356284,  709706295,
  1453549767, 591603172,  768512391,  854125182
]
