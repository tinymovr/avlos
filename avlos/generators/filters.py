import os
from copy import copy


def avlos_endpoints(input):
    """
    Traverse remote dictionary and return list
    of remote endpoints
    """
    def traverse_endpoint_list(ep_list, ep_out_list):
        for ep in ep_list:
            if (
                hasattr(ep, "getter_name")
                or hasattr(ep, "setter_name")
                or hasattr(ep, "caller_name")
            ):
                ep_out_list.append(ep)
            elif hasattr(ep, "remote_attributes"):
                traverse_endpoint_list(ep.remote_attributes.values(), ep_out_list)

    ep_out_list = []
    if hasattr(input, "remote_attributes"):
        traverse_endpoint_list(input.remote_attributes.values(), ep_out_list)
    return ep_out_list


def avlos_enum_eps(input):
    """
    Traverse remote dictionary and return a list of enum type endpoints
    """
    return [ep for ep in avlos_endpoints(input) if hasattr(ep, "options")]


def avlos_bitmask_eps(input):
    """
    Traverse remote dictionary and return a list of bitmask type endpoints
    """
    return [ep for ep in avlos_endpoints(input) if hasattr(ep, "bitmask")]


def as_include(input):
    """
    Render a string as a C include, with opening
    and closing braces or quotation marks
    """
    if input.startswith('"') and input.endswith('"'):
        return input
    elif input.startswith("<") and input.endswith(">"):
        return input
    return "<" + input + ">"


def file_from_path(input):
    """
    Get the file string from a path string
    """
    return os.path.basename(input)


def capitalize_first(input):
    """
    Capitalize the first character of a
    string, leaving the rest unchanged
    """
    return input[0].upper() + input[1:]
