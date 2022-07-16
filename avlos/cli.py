"""Avlos CLI

Usage:
    avlos from (file <spec_path> | url <spec_url>) [--config=<config_path>]
    avlos -h | --help
    avlos --version

Options:
    --config=<config_path>  Path of the Avlos config file [default: ./avlos_config.yaml]
"""

import yaml
from typing import Dict
import logging
import pkg_resources
import urllib.request
from docopt import docopt
from avlos.deserializer import deserialize
from avlos.processor import process_with_config_file

shell_name = "Avlos"


def run_cli():
    """
    Runs the Avlos CLI
    """
    version: str = pkg_resources.require("avlos")[0].version
    arguments: Dict[str, str] = docopt(__doc__, version=shell_name + " " + str(version))

    logger = configure_logging()

    config_path: str = arguments["--config"]

    if arguments["<spec_path>"]:
        with open(arguments["<spec_path>"]) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))
            process_with_config_file(obj, config_path, traverse_path=True)
    elif arguments["<spec_url>"]:
        device_desc_string = urllib.request.urlopen(arguments["<spec_url>"]).read()
        obj = deserialize(yaml.safe_load(device_desc_string))
        process_with_config_file(obj, config_path, traverse_path=True)


def configure_logging() -> logging.Logger:
    """
    Configures logging options and
    generates a default logger instance.
    """
    logger = logging.getLogger("avlos")
    logger.setLevel(logging.DEBUG)
    return logger
