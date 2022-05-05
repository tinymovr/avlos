from rstcloth import RstCloth


def process(instance, config):

    
    with open(config["paths"]["output_file"], "w") as output_file:
        d = RstCloth(stream=output_file)
        state = {"ep_counter": 1, "prefix": ""}

        d.ref_target("api-reference")
        d.newline()
        d.h2("API Reference")

        traverse(instance, state, d)


def traverse(obj, state, d):
    try:
        current_prefix = state["prefix"]
        for child in obj.remote_attributes.values():
            state["prefix"] = "{}{}.".format(current_prefix, obj.name)
            traverse(child, state, d)
        state["prefix"] = current_prefix
    except AttributeError:
        d.newline()
        if None != obj.rst_target:
            d.ref_target(obj.rst_target)
            d.newline()
        d.h2("{}{}".format(state["prefix"], obj.name))
        d.newline()
        d.li("Endpoint ID: {}".format(state["ep_counter"]))
        d.li("Data Type: {}".format(obj.dtype))
        d.li("Unit: {}".format(obj.unit.units if obj.unit != None else "Not defined"))
        d.newline()
        d.content(obj.description)
        d.newline()

        state["ep_counter"] += 1


# .. _api-reference:

# API Reference
# #############

# .. note::
#     Where "float32" is mentioned, an IEEE 754, 32-bit floating point representation is assumed.
