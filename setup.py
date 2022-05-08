#!/usr/bin/env python

import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

extras_generator_c = ["csnake"]
extras_generator_rst = ["rstcloth"]
extras_generator_cpp = ["jinja2"]
extras_all = extras_generator_c + extras_generator_rst + extras_generator_cpp

setup(
    name="Avlos",
    version="0.1",
    description="Avlos Remote Object Templating System",
    author="Yannis Chatzikonstantinou",
    author_email="yannis@tinymovr.com",
    url="https://www.tinymovr.com",
    packages=find_packages(include=["avlos", "avlos.*"]),
    python_requires=">=3.6",
    install_requires=["marshmallow", "pyyaml", "pint", "docopt"],
    entry_points={"console_scripts": ["avlos=avlos.cli:run_cli"]},
    extras_require={
        "generator_c": extras_generator_c,
        "generator_rst": extras_generator_rst,
        "generator_cpp": extras_generator_cpp,
        'all': extras_all
    },
)
