# -*- coding: utf-8 -*-
import mmap
import click
from fastcdc import __version__, FastCDC
from hashlib import sha256


@click.command("fastcdc", no_args_is_help=True)
@click.version_option(version=__version__, message="fastcdc - %(version)s")
@click.argument("file", type=click.File("rb"))
@click.option(
    "-s",
    "--size",
    type=click.INT,
    default=8192,
    help="The desired average size of the chunks.",
    show_default=True,
)
def cli(file, size):
    """Splits a (large) file and computes sha256 hashes."""
    min_size = size // 2
    max_size = size * 2
    with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        chunker = FastCDC.new(mm, min_size, size, max_size)
        for chunk in chunker:
            end = chunk.offset + chunk.length
            digest = sha256(mm[chunk.offset : end]).hexdigest()
            click.secho("hash", fg="bright_magenta", nl=False)
            click.secho("=", nl=False)
            click.secho(digest, fg="bright_cyan", nl=False)
            click.secho(" offset", fg="bright_magenta", nl=False)
            click.secho("=", nl=False)
            click.secho(str(chunk.offset), fg="bright_cyan", nl=False)
            click.secho(" size", fg="bright_magenta", nl=False)
            click.secho("=", nl=False)
            click.secho(str(chunk.length), fg="bright_cyan")


if __name__ == "__main__":
    cli()
