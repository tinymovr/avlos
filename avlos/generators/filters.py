import os
from copy import copy
from typing import List


def avlos_endpoints(input) -> List:
    """
    Traverse remote dictionary and return list of remote endpoints.

    Recursively walks the tree of RemoteNode objects and collects all endpoint
    objects (those with getter_name, setter_name, or caller_name).

    Args:
        input: Root RemoteNode to traverse

    Returns:
        Flat list of all endpoint objects found in the tree
    """

    def traverse_endpoint_list(ep_list, ep_out_list: List) -> None:
        """Helper function to recursively traverse endpoint tree."""
        for ep in ep_list:
            if hasattr(ep, "getter_name") or hasattr(ep, "setter_name") or hasattr(ep, "caller_name"):
                ep_out_list.append(ep)
            elif hasattr(ep, "remote_attributes"):
                traverse_endpoint_list(ep.remote_attributes.values(), ep_out_list)

    ep_out_list: List = []
    if hasattr(input, "remote_attributes"):
        traverse_endpoint_list(input.remote_attributes.values(), ep_out_list)
    return ep_out_list


def avlos_enum_eps(input) -> List:
    """
    Traverse remote dictionary and return a list of enum type endpoints.

    Args:
        input: Root RemoteNode to traverse

    Returns:
        List of RemoteEnum objects
    """
    return [ep for ep in avlos_endpoints(input) if hasattr(ep, "options")]


def avlos_bitmask_eps(input) -> List:
    """
    Traverse remote dictionary and return a list of bitmask type endpoints.

    Args:
        input: Root RemoteNode to traverse

    Returns:
        List of RemoteBitmask objects
    """
    return [ep for ep in avlos_endpoints(input) if hasattr(ep, "bitmask")]


def as_include(input: str) -> str:
    """
    Render a string as a C include, with opening and closing braces or quotation marks.

    If the input already has proper include delimiters, returns unchanged.
    Otherwise, wraps in angle brackets.

    Args:
        input: Include path string

    Returns:
        Properly formatted include directive (e.g., "<stdio.h>" or '"myheader.h"')
    """
    if input.startswith('"') and input.endswith('"'):
        return input
    elif input.startswith("<") and input.endswith(">"):
        return input
    return "<" + input + ">"


def file_from_path(input: str) -> str:
    """
    Get the file string from a path string.

    Args:
        input: File path

    Returns:
        Base filename without directory path
    """
    return os.path.basename(input)


def capitalize_first(input: str) -> str:
    """
    Capitalize the first character of a string, leaving the rest unchanged.

    Args:
        input: String to capitalize

    Returns:
        String with first character capitalized
    """
    return input[0].upper() + input[1:]
