__version__ = "1.1.0"
from fastcdc.original import FastCDC

try:
    from fastcdc.cli import chunkify
except ImportError:
    from fastcdc.lib import chunkify
