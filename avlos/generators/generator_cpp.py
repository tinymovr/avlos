import os
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape
import avlos
from avlos.generators.type_map import c_type_map as type_map


env = Environment(loader=PackageLoader("avlos"), autoescape=select_autoescape())


def process(instance, config):
    process_header(instance, config)
    process_impl(instance, config)


def process_header(instance, config):
    template = env.get_template("tinymovr.hpp.jinja")
    file = os.path.join(
        os.path.dirname(config["paths"]["output_dir"]),
        "tinymovr.hpp",
    )
    try:
        includes = config["cpp_header_includes"]
    except KeyError:
        includes = []
    with open(file, "w") as output_file:
        print(
            template.render(instance=instance, type_map=type_map, includes=includes),
            file=output_file,
        )
    for attr in instance.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_header(attr, config)


def recurse_header(remote_object, config):
    template = env.get_template("remote_object.hpp.jinja")
    file = os.path.join(
        os.path.dirname(config["paths"]["output_dir"]),
        remote_object.name + ".hpp",
    )
    with open(file, "w") as output_file:
        print(
            template.render(instance=remote_object, type_map=type_map), file=output_file
        )
    for attr in remote_object.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_header(attr, config)


def process_impl(instance, config):
    template = env.get_template("tinymovr.cpp.jinja")
    file = os.path.join(
        os.path.dirname(config["paths"]["output_dir"]),
        "tinymovr.cpp",
    )
    try:
        includes = config["cpp_impl_includes"]
    except KeyError:
        includes = []
    with open(file, "w") as output_file:
        print(
            template.render(instance=instance, type_map=type_map, includes=includes),
            file=output_file,
        )
    for attr in instance.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_impl(attr, config)


def recurse_impl(remote_object, config):
    template = env.get_template("remote_object.cpp.jinja")
    file = os.path.join(
        os.path.dirname(config["paths"]["output_dir"]),
        remote_object.name + ".cpp",
    )
    with open(file, "w") as output_file:
        print(
            template.render(instance=remote_object, type_map=type_map), file=output_file
        )
    for attr in remote_object.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_impl(attr, config)
