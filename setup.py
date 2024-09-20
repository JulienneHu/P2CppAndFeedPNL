from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "black_scholes",
        ["black_scholes.cpp"],
    ),
]

setup(
    name="black_scholes",
    version="1.0",
    author="Jun Hu",
    description="Python bindings for Black Scholes model using pybind11",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)

# command to build the extension module
# python setup.py build_ext --inplace