import os
import sys

from jinja2 import Environment, PackageLoader, select_autoescape

from avlos.formatting import format_c_code, is_clang_format_available
from avlos.generators.filters import as_include, avlos_bitmask_eps, avlos_endpoints, avlos_enum_eps
from avlos.validation import ValidationError, validate_all

env = Environment(loader=PackageLoader("avlos"), autoescape=select_autoescape())


def process(instance, config):
    # Validate before generation
    validation_errors = validate_all(instance)
    if validation_errors:
        error_msg = "Validation failed:\n" + "\n".join(f"  - {err}" for err in validation_errors)
        raise ValidationError(error_msg)

    env.filters["endpoints"] = avlos_endpoints
    env.filters["enum_eps"] = avlos_enum_eps
    env.filters["bitmask_eps"] = avlos_bitmask_eps
    env.filters["as_include"] = as_include

    template = env.get_template("tm_enums.h.jinja")
    os.makedirs(os.path.dirname(config["paths"]["output_enums"]), exist_ok=True)
    with open(config["paths"]["output_enums"], "w") as output_file:
        print(
            template.render(instance=instance),
            file=output_file,
        )

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

    # Post-process with clang-format if available
    format_style = config.get("format_style", "LLVM")

    generated_files = [
        config["paths"]["output_enums"],
        config["paths"]["output_header"],
        config["paths"]["output_impl"],
    ]

    for file_path in generated_files:
        success = format_c_code(file_path, format_style)
        if not success and is_clang_format_available():
            # Only warn if clang-format is installed but failed
            print(f"Warning: clang-format failed for {file_path}", file=sys.stderr)
