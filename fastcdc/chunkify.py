# -*- coding: utf-8 -*-
import click
from fastcdc import __version__, fastcdc
import hashlib
from fastcdc.utils import DefaultHelp, supported_hashes


@click.command(cls=DefaultHelp)
@click.version_option(version=__version__, message="fastcdc - %(version)s")
@click.argument("file", type=click.File("rb"))
@click.option(
    "-s",
    "--size",
    type=click.INT,
    default=16384,
    help="The desired average size of the chunks.",
    show_default=True,
)
@click.option(
    "-mi", "--min-size", type=click.INT, help="Minimum chunk size (default size/4)"
)
@click.option(
    "-ma", "--max-size", type=click.INT, help="Maximum chunk size (default size*8)"
)
@click.option(
    "-hf", "--hash-function", type=click.STRING, default="sha256", show_default=True
)
def chunkify(file, size, min_size, max_size, hash_function):
    """Find variable sized chunks for FILE and compute hashes."""
    supported = supported_hashes()
    if hash_function not in supported:
        msg = "'{}' is not a supported hash.\nTry one of these:\n{}".format(
            hash_function, ", ".join(supported)
        )
        raise click.BadOptionUsage("hf", msg)

    hf = getattr(hashlib, hash_function)
    chunker = fastcdc(file, min_size, size, max_size, hf=hf)

    num_chunks = 0
    for chunk in chunker:
        click.secho("hash", fg="bright_magenta", nl=False)
        click.secho("=", nl=False)
        click.secho(chunk.hash, fg="bright_cyan", nl=False)
        click.secho(" offset", fg="bright_magenta", nl=False)
        click.secho("=", nl=False)
        click.secho(str(chunk.offset), fg="bright_cyan", nl=False)
        click.secho(" size", fg="bright_magenta", nl=False)
        click.secho("=", nl=False)
        click.secho(str(chunk.length), fg="bright_cyan")
        num_chunks += 1
