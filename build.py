# -*- coding: utf-8 -*-
"""
The shared library can also be built manually using the command:
$ cythonize -X language_level=3 -a -i ./fastcdc/fastcdc_cy.pyx
"""
from distutils.command.build_ext import build_ext


class BuildExt(build_ext):
    def run(self):
        try:
            print("Trying to compile C accelerator module")
            build_ext.run(self)
            print("Successfully comiled C accelerator module")
        except Exception as e:
            print(e)
            print("************************************************************")
            print("Cannot compile C accelerator module, use pure python version")
            print("************************************************************")

    def build_extensions(self):
        try:
            print("Trying to compile C accelerator module")
            super().build_extensions()
            print("Successfully comiled C accelerator module")
        except Exception as e:
            print(e)
            print("************************************************************")
            print("Cannot compile C accelerator module, use pure python version")
            print("************************************************************")


def build(setup_kwargs):
    try:
        from Cython.Build import cythonize

        setup_kwargs.update(
            dict(
                ext_modules=cythonize(["fastcdc/fastcdc_cy.pyx"]),
                cmdclass=dict(build_ext=BuildExt),
            )
        )
    except Exception as e:
        print(e)
        print("************************************************************")
        print("Cannot compile C accelerator module, use pure python version")
        print("************************************************************")
