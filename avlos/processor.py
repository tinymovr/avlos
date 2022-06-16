from os.path import join, dirname, realpath
import yaml
from importlib import import_module


def process_with_config_file(device_instance, output_config_path):
    """
    Process a device spec using an output config path.
    """
    with open(output_config_path) as output_config_stream:
        output_config = yaml.safe_load(output_config_stream)
        for module_config in output_config["generators"].values():
            # Convert all paths to absolute using the base path
            for path_name, path in module_config["paths"].items():
                module_config["paths"][path_name] = realpath(
                    join(dirname(realpath(output_config_path)), path)
                )
    process_with_config_object(device_instance, output_config)


def process_with_config_object(device_instance, output_config):
    """
    Process a device spec using an output config object.
    """
    for module_name, module_config in output_config["generators"].items():
        if "enabled" in module_config and True == module_config["enabled"]:
            generator = import_module(
                ".generators.{}".format(module_name), package="avlos"
            )
            generator.process(device_instance, module_config)

