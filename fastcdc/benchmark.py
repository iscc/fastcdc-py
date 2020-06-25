# -*- coding: utf-8 -*-
import os
import platform
from statistics import mean
import click
from humanize import naturalsize as nsize
from codetiming import Timer
import cpuinfo
import fastcdc


def system_info():
    """Printable system info"""
    cinfo = cpuinfo.get_cpu_info()
    sinfo = (
        "FastCDC Performance Benchmark\n"
        "==========================================================================\n"
        "CPU:     {}\n"
        "Cores:   {}\n"
        "OS:      {}\n"
        "Python:  {} - {} - {}\n"
        "FastCDC: {}\n"
        "==========================================================================\n"
    ).format(
        cinfo.get("brand_raw"),
        cinfo.get("count"),
        platform.platform(),
        platform.python_implementation(),
        platform.python_version(),
        platform.python_compiler(),
        fastcdc.__version__,
    )
    return sinfo


@click.command("benchmark")
def benchmark():
    """Benchmark chunking performance."""
    files = [os.urandom(4194304) for _ in range(64)]
    num_bytes = 4194304

    print(system_info())

    from fastcdc.fastcdc_py import fastcdc_py

    chunk_funks = [fastcdc_py]
    try:
        from fastcdc.fastcdc_cy import fastcdc_cy

        chunk_funks.append(fastcdc_cy)
    except ImportError:
        click.echo("Skip native cython version")

    chunk_sizes = (1024, 2048, 4096, 8192, 16384, 32768, 65536)

    result = []
    for avg_size in chunk_sizes:
        click.echo("Chunksize:  {}".format(nsize(avg_size)))
        for func in chunk_funks:
            timer_name = "{}_{}".format(func.__name__, avg_size)
            t = Timer(timer_name, logger=None)
            for file in files:
                t.start()
                result = list(func(file, avg_size=avg_size))
                t.stop()
            data_per_s = num_bytes / Timer.timers.mean(timer_name)
            click.echo("{}: {}/s".format(func.__name__, nsize(data_per_s)))
        avg_size = mean([c.length for c in result])
        click.echo("Real AVG:  {}".format(nsize(avg_size)))
        click.echo()


if __name__ == "__main__":
    benchmark()
