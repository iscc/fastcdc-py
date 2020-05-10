# -*- coding: utf-8 -*-
"""
The shared library can also be built manually using the command:
$ cythonize -X language_level=3 -a -i ./fastcdc/cylib.py
"""
from distutils.command.build_ext import build_ext


class BuildExt(build_ext):
    def build_extensions(self):
        try:
            super().build_extensions()
        except Exception:
            pass


def build(setup_kwargs):
    try:
        from Cython.Build import cythonize

        setup_kwargs.update(
            dict(
                ext_modules=cythonize(["fastcdc/cylib.py"]),
                cmdclass=dict(build_ext=BuildExt),
            )
        )
    except Exception:
        print("Skipped building cython extension module.")
