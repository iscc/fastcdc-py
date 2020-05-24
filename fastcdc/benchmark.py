# -*- coding: utf-8 -*-
import os
from statistics import mean
import click
from humanize import naturalsize as nsize
from codetiming import Timer
import cpuinfo


@click.command("benchmark")
def benchmark():
    """Benchmark chunking performance."""
    cinfo = cpuinfo.get_cpu_info()
    click.echo()
    click.echo("CPU:   {}".format(cinfo.get("brand")))
    click.echo("Cores: {}".format(cinfo.get("count")))
    click.echo("=" * 88)

    from fastcdc.fastcdc_py import fastcdc_py

    chunk_funks = [fastcdc_py]
    try:
        from fastcdc.fastcdc_cy import fastcdc_cy

        chunk_funks.append(fastcdc_cy)
    except ImportError:
        click.echo("Skip native cython version")

    chunk_sizes = (2048, 4096, 8192, 16384, 32768, 65536, 131072)

    MB = 1_000_000
    num_bytes = 100 * MB

    data = os.urandom(num_bytes)
    for avg_size in chunk_sizes:
        click.echo("Chunksize:  {}".format(nsize(avg_size)))
        for func in chunk_funks:
            t = Timer(logger=None)
            t.start()
            result = list(func(data, avg_size=avg_size))
            t.stop()
            data_per_s = num_bytes / t.last
            click.echo("{}: {}/s".format(func.__name__, nsize(data_per_s)))
        avg_size = mean([c.length for c in result])
        click.echo("Real AVG:  {}".format(nsize(avg_size)))
        click.echo()
