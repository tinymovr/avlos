

def avlos_endpoints(input):
    """
    Traverse remote dictionary and return list
    of remote endpoints
    """
    def traverse_endpoint_list(ep_list, ep_out_list):
        for ep in ep_list:
            if hasattr(ep, "c_getter") or hasattr(ep, "c_setter"):
                ep_out_list.append(ep)
            elif hasattr(ep, "remote_attributes"):
                traverse_endpoint_list(ep.remote_attributes.values(), ep_out_list)
    ep_out_list = []
    if hasattr(input, "remote_attributes"):
        traverse_endpoint_list(input.remote_attributes.values(), ep_out_list)
    return ep_out_list


def as_include(input):
    """
    Render a string as a C include, with opening
    and closing braces or quotation marks
    """
    if input.startswith("\"") and input.endswith("\""):
        return input
    elif input.startswith("<") and input.endswith(">"):
        return input
    return "<" + input + ">"