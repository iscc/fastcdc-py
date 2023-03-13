# -*- coding: utf-8 -*-
import click


try:
    from fastcdc.fastcdc_cy import fastcdc_cy as fastcdc
except ImportError:
    from fastcdc.fastcdc_py import fastcdc_py as fastcdc

    click.secho("Running in pure python mode (slow)", fg="bright_magenta")

__version__ = "1.5.0"
