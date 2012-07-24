from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


with open('README.txt') as file:
    long_description = file.read()

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("plyr", ["src/glyr.pyx"], libraries=['glyr'])],
    name='plyr',
    version='0.9.9',
    author='Christopher Pahl',
    author_email='sahib@online.de',
    url='http://sahib.github.com/python-glyr/intro.html',
    long_description=long_description
)
