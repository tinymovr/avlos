from jinja2 import Environment, PackageLoader, select_autoescape
from avlos.generators.filters import avlos_endpoints

env = Environment(loader=PackageLoader("avlos"), autoescape=select_autoescape())


def process(instance, config):
    env.filters["endpoints"] = avlos_endpoints

    template = env.get_template("docs.rst.jinja")
    with open(config["paths"]["output_file"], "w+") as output_file:
        print(
            template.render(instance=instance),
            file=output_file,
        )
