import os
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(loader=PackageLoader("avlos"), autoescape=select_autoescape())


def process(instance, config):
    process_header(instance, config)
    process_impl(instance, config)


def process_header(instance, config):
    template = env.get_template("device.hpp.jinja")
    file = config["paths"]["output_header"]
    try:
        includes = config["cpp_header_includes"]
    except KeyError:
        includes = []
    with open(file, "w") as output_file:
        print(
            template.render(instance=instance, includes=includes),
            file=output_file,
        )
    for attr in instance.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_header(attr, config)


def recurse_header(remote_object, config):
    template = env.get_template("remote_object.hpp.jinja")
    file = os.path.join(
        os.path.dirname(config["paths"]["output_header"]),
        remote_object.name + ".hpp",
    )
    with open(file, "w") as output_file:
        print(template.render(instance=remote_object), file=output_file)
    for attr in remote_object.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_header(attr, config)


def process_impl(instance, config):
    template = env.get_template("device.cpp.jinja")
    file = config["paths"]["output_impl"]
    try:
        includes = config["cpp_impl_includes"]
    except KeyError:
        includes = []
    with open(file, "w") as output_file:
        print(
            template.render(instance=instance, includes=includes),
            file=output_file,
        )
    for attr in instance.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_impl(attr, config)


def recurse_impl(remote_object, config):
    template = env.get_template("remote_object.cpp.jinja")
    file = os.path.join(
        os.path.dirname(config["paths"]["output_impl"]),
        remote_object.name + ".cpp",
    )
    with open(file, "w") as output_file:
        print(template.render(instance=remote_object), file=output_file)
    for attr in remote_object.remote_attributes.values():
        if hasattr(attr, "remote_attributes"):
            recurse_impl(attr, config)
