# -*- coding: utf-8 -*-
import click
from fastcdc import __version__, fastcdc
import hashlib


@click.command("fastcdc", no_args_is_help=True)
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
def cli(file, size, min_size, max_size, hash_function):
    """Splits a (large) file into variable sized chunks and computes hashes."""
    supported = list(hashlib.algorithms_guaranteed)
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


if __name__ == "__main__":
    cli()
