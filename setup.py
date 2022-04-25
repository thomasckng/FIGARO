import numpy
from setuptools import setup, find_packages
from setuptools import Extension
from setuptools.command.build_ext import build_ext as _build_ext
from codecs import open
from os import path
from distutils.extension import Extension
import os
import warnings

if not("LAL_DATADIR" in os.environ):
    lal_flag = False
else:
    lal_flag   = True
    
try:
    from Cython.Build import cythonize
except:
    print('Cython not found. Please install it via\n\tpip install Cython')
    exit()

with open("requirements.txt") as requires_file:
    requirements = requires_file.read().split("\n")

# see https://stackoverflow.com/a/21621689/1862861 for why this is here
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        self.include_dirs.append(numpy.get_include())

ext_modules=[
             Extension("figaro.cumulative",
                       sources=[os.path.join("figaro","cumulative.pyx")],
                       libraries=["m"], # Unix-like specific
                       extra_compile_args=["-O3","-ffast-math"],
                       include_dirs=['figaro', numpy.get_include()]
                       ),
            ]
if lal_flag:
    ext_modules.append(Extension("figaro.cosmology",
                       sources=[os.path.join("figaro","cosmology.pyx")],
                       libraries=["m", "lal"], # Unix-like specific
                       extra_compile_args=["-O3","-ffast-math"],
                       include_dirs=['figaro', numpy.get_include()]
                       ))

ext_modules = cythonize(ext_modules, compiler_directives={'language_level' : "3"})
setup(
      name = 'figaro/cumulative',
      ext_modules = cythonize(ext_modules, language_level = "3"),
      include_dirs=['figaro', numpy.get_include()]
      )
if lal_flag:
    setup(
          name = 'figaro/cosmology',
          ext_modules = cythonize(ext_modules, language_level = "3"),
          include_dirs=['figaro', numpy.get_include()]
          )

setup(
    name = 'figaro',
    description = 'FIGARO: Fast Inference for GW Astronomy, Research & Observations',
    author = 'Walter Del Pozzo, Stefano Rinaldi',
    author_email = 'walter.delpozzo@unipi.it, stefano.rinaldi@phd.unipi.it',
    url = 'https://git.ligo.org/stefano.rinaldi/online-localisation',
    python_requires = '>=3.7',
    packages = ['figaro'],
    install_requires=requirements,
    include_dirs = ['figaro', numpy.get_include()],
    setup_requires=['numpy', 'cython'],
    entry_points={},
    package_data={"": ['*.c', '*.pyx', '*.pxd']},
    ext_modules=ext_modules,
    )

if not lal_flag:
    warnings.warn("No LAL installation found, please install LAL - see https://wiki.ligo.org/Computing/LALSuiteInstall. Some functions - GW posterior samples loading and catalog loading - won't be available and errors might be raised.")
