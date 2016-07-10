from setuptools import setup, find_packages

setup(
    name="nsemodule",
    version="0.7",
    author="Raj Patel",
    author_email="rajpateld001@gmail.com",
    description = ("Python library for extracting realtime data from National Stock Exchange"),
    license="MIT",
    keywords="nse quote market",
    install_requires=['six'],
    url ="https://github.com/muepsilon/nsemodule",
    packages = ['nsemodule'],
    package_dir={'nsemodule': 'src/nsemodule'},
)