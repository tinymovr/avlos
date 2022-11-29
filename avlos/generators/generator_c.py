import os
from jinja2 import Environment, PackageLoader, select_autoescape
from avlos.generators.filters import (
    avlos_endpoints,
    avlos_bitmask_eps,
    as_include,
    file_from_path,
)

env = Environment(loader=PackageLoader("avlos"), autoescape=select_autoescape())


def process(instance, config):
    env.filters["endpoints"] = avlos_endpoints
    env.filters["bitmask_eps"] = avlos_bitmask_eps
    env.filters["as_include"] = as_include

    template = env.get_template("fw_endpoints.h.jinja")
    try:
        includes = config["header_includes"]
    except KeyError:
        includes = []
    os.makedirs(os.path.dirname(config["paths"]["output_header"]), exist_ok=True)
    with open(config["paths"]["output_header"], "w") as output_file:
        print(
            template.render(instance=instance, includes=includes),
            file=output_file,
        )

    template = env.get_template("fw_endpoints.c.jinja")
    try:
        includes = config["impl_includes"]
    except KeyError:
        includes = []
    os.makedirs(os.path.dirname(config["paths"]["output_impl"]), exist_ok=True)
    with open(config["paths"]["output_impl"], "w") as output_file:
        print(
            template.render(instance=instance, includes=includes),
            file=output_file,
        )
