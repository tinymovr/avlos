#!/usr/bin/env python

import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="Avlos",
    use_scm_version={
        "write_to": "avlos/_version.py",
        "write_to_template": '__version__ = "{version}"\n',
    },
    description="Generate type-safe communication protocols for embedded systems from a single YAML specification",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Yannis Chatzikonstantinou",
    author_email="yannis@tinymovr.com",
    url="https://www.tinymovr.com",
    packages=find_packages(include=["avlos", "avlos.*"]),
    include_package_data=True,
    python_requires=">=3.9",
    setup_requires=["setuptools_scm"],
    install_requires=["marshmallow", "pyyaml", "pint", "docopt", "jinja2"],
    extras_require={"dev": ["rstcheck"]},
    entry_points={"console_scripts": ["avlos=avlos.cli:run_cli"]},
)
