from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

print("""Please make sure to:
- Have libglyr >= 1.0.0 and all developement deps installed.
- Have a working compiler.

Cython will be installed automatically.
""")

with open('README.txt') as file:
    long_description = file.read()

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("plyr", ["src/glyr.pyx"], libraries=['glyr'])],
    name='plyr',
    version='1.0.0',
    author='Christopher Pahl',
    author_email='sahib@online.de',
    url='http://sahib.github.com/python-glyr/intro.html',
    long_description=long_description
)
