#!/usr/bin/env python
# setup.py file for glyr's python bindings
# Run with: python setup.py build_ext --inplace

from distutils.core import setup, Extension

#######################################################
# Build a SWIG Module using build_ext
# NOTE: If you have glyr headers installed 
#       in a non-standard location you might want 
#       to change the INCLUDE_PATH variable accordingly
#######################################################
INCLUDE_PATH   = '-I/usr/include'
MODULE_C_NAME  = 'cglyr'
MODULE_PY_NAME = 'glyr'

glypy_module = Extension(name              = '_' + MODULE_C_NAME,
                        sources            = ['ext/python_glyr.i'],
                        libraries          = [MODULE_PY_NAME],
                        swig_opts          = ['-modern','-Wextra','-outdir','src/' + MODULE_PY_NAME, INCLUDE_PATH],
                        # Disable warnings (which often discomfort normal users :)) for autocompile code
                        extra_compile_args = ['-Wno-unused-label','-Wno-unused-but-set-variable','-ggdb3']
                        )

setup(
        name         = MODULE_PY_NAME,
        version      = '0.1',
        author       = 'sahib',
        author_email = 'sahib@online.de',
        description  = 'Python bindings to libglyr',
        packages     = [MODULE_PY_NAME],
        package_dir  = {'': 'src'},
        ext_modules  = [glypy_module],
        ext_package  = MODULE_PY_NAME,
        py_modules   = [MODULE_C_NAME,MODULE_PY_NAME],
        )
