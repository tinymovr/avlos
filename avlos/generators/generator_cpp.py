import os``
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape
import avlos
from avlos.generators.type_map import c_type_map


env = Environment(loader=PackageLoader("avlos"), autoescape=select_autoescape())


def process(instance, config):
    process_header(instance, config)
    process_impl(instance, config)


def process_header(instance, config):
    template = env.get_template("tinymovr.hpp")
    with open(config["paths"]["output_header"], "w") as output_file:
        print(template.render(instance=instance), file=output_file)
    for object in instance["remote_attributes"]:
        recurse_header(object, config)


def recurse_header(remote_object, config):
    template = env.get_template("remote_object.hpp")
    file = os.path.join(Path(config["paths"]["output_header"]).resolve(), remote_object["name"])
    with open(file, "w") as output_file:
        print(template.render(instance=remote_object), file=output_file)


def process_impl(instance, config):
    template = env.get_template("tinymovr.cpp")
    with open(config["paths"]["output_impl"], "w") as output_file:
        print(template.render(instance=instance), file=output_file)


def recurse_impl(remote_object, config):
    template = env.get_template("remote_object.cpp")
    file = os.path.join(Path(config["paths"]["output_impl"]).resolve(), remote_object["name"])
    with open(file, "w") as output_file:
        print(template.render(instance=remote_object), file=output_file)
