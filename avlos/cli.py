"""Avlos CLI

Usage:
    avlos <spec_path> [--config=<config_path>]
    avlos -h | --help
    avlos --version

Options:
    --config=<config_path>  Path of the Avlos config file [default: ./avlos_config.yaml]
"""

import yaml
from typing import Dict
import logging
import pkg_resources
from docopt import docopt
from avlos.deserializer import deserialize
from avlos.processor import process_file

shell_name = "Avlos"


def run_cli():
    version: str = pkg_resources.require("avlos")[0].version
    arguments: Dict[str, str] = docopt(__doc__, version=shell_name + " " + str(version))

    logger = configure_logging()

    spec_path: str = arguments["<spec_path>"]
    config_path: str = arguments["--config"]
    with open(spec_path) as device_desc_stream:
        obj = deserialize(yaml.safe_load(device_desc_stream))
        process_file(obj, config_path)


def configure_logging() -> logging.Logger:
    """
    Configures logging options and
    generates a default logger instance.
    """
    logger = logging.getLogger("avlos")
    logger.setLevel(logging.DEBUG)
    return logger
