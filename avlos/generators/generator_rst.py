
from rstcloth import RstCloth


def process(instance, config):    

    d = RstCloth()
    state = {
        "ep_counter": 1,
        "prefix": ""
        }
    
    traverse(instance, state, d)
    d.write(config["paths"]["output_file"])


def traverse(obj, state, d):
    try:
        current_prefix = state["prefix"]
        for child in obj.children.values():
            state["prefix"] = "{}{}.".format(current_prefix, obj.name)
            traverse(child, state, d)
        state["prefix"] = current_prefix
    except AttributeError:
        d.newline()
        d.h2("{}{}".format(state["prefix"], obj.name))
        d.newline()
        d.li("Endpoint ID: {}".format(state["ep_counter"]))
        d.li("Data Type: {}".format(obj.dtype))
        d.li("Unit: {}".format(obj.unit if obj.unit else "Not defined"))
        d.newline()
        d.content(obj.description)

        state["ep_counter"] += 1