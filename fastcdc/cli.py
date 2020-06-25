# -*- coding: utf-8 -*-
import click
from click_default_group import DefaultGroup
from fastcdc import __version__
from fastcdc import chunkify
from fastcdc import benchmark
from fastcdc import scan


@click.group(cls=DefaultGroup, default="chunkify", default_if_no_args=False)
@click.version_option(version=__version__, message="fastcdc - %(version)s")
def cli():
    pass


cli.add_command(chunkify.chunkify)
cli.add_command(benchmark.benchmark)
cli.add_command(scan.scan)

if __name__ == "__main__":
    cli()
