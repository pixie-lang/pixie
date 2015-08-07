from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="pixie",
    version="0.2.0",
    description="A fast lightweight lisp with 'magical' powers",

    license="LGPL",

    keywords="development language",

    package_data={"pixie": ["libpixie-vm.dylib", "pixie-vm"]}
)