from os.path import join, dirname, basename, realpath
import yaml
from importlib import import_module


def process_with_config_file(device_instance, avlos_config_path, traverse_path=False):
    """
    Process a device spec using an output config path.
    """
    real_path = realpath(avlos_config_path)
    avlos_config = None
    while not avlos_config:
        try:
            with open(real_path) as avlos_config_stream:
                avlos_config = yaml.safe_load(avlos_config_stream)
        except FileNotFoundError as e:
            if traverse_path:
                # traverse path backwards
                new_config_path = join(dirname(real_path), "..", basename(real_path))
                if new_config_path == real_path:
                    # we're at the root, and have not found the file
                    raise FileNotFoundError from e
                real_path = new_config_path
            else:
                raise e

    for module_config in avlos_config["generators"].values():
        # Convert all paths to absolute using the base path
        for path_name, path in module_config["paths"].items():
            module_config["paths"][path_name] = realpath(join(dirname(real_path), path))
    process_with_config_object(device_instance, avlos_config)


def process_with_config_object(device_instance, avlos_config):
    """
    Process a device spec using an output config object.
    """
    for module_name, module_config in avlos_config["generators"].items():
        if "enabled" in module_config and True == module_config["enabled"]:
            generator = import_module(
                ".generators.{}".format(module_name), package="avlos"
            )
            generator.process(device_instance, module_config)
