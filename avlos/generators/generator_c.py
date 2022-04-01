import os
import avlos
from csnake import CodeWriter, Function, FuncPtr, Variable, AddressOf, FormattedLiteral


c_type_map = {
    "bool": "bool",
    "int8": "int8_t",
    "uint8": "uint8_t",
    "int16": "int16_t",
    "uint16": "uint16_t",
    "int32": "int32_t",
    "uint32": "uint32_t",
    "float": "float",
}


def process(instance, config):
    process_header(instance, config)
    process_impl(instance, config)


def process_header(instance, config):
    cw_head = CodeWriter()
    cw_head.add_autogen_comment()
    cw_head.add_line("")

    # Imports
    try:
        for header in config["c_includes"]:
            cw_head.include(header)
        cw_head.add_line("")
    except KeyError:
        pass

    # Function prototypes
    state = {"ep_counter": 1}  # Reset state
    traverse_header(instance, state, cw_head)
    # TODO: Make below declaration safer
    cw_head.add_line(
        "uint8_t avlos_get_hash(uint8_t * buffer, uint8_t * buffer_len, bool rtr);"
    )
    cw_head.add_line("")

    # Function list
    state = {"f_list": []}  # Reset state
    traverse_function_list(instance, state, cw_head)
    state["f_list"].append(
        AddressOf(Variable("avlos_get_hash", FuncPtr("uint8_t", arguments=get_args())))
    )
    output_function_array(state["f_list"], cw_head)

    # Write out
    with open(config["paths"]["output_header"], "w") as output_file:
        print(cw_head, file=output_file)


def process_impl(instance, config):
    cw_impl = CodeWriter()
    cw_impl.add_autogen_comment()
    cw_impl.add_line("")

    # Includes
    cw_impl.include(config["paths"]["output_header"])
    cw_impl.add_line("")

    # Implementations
    state = {"ep_counter": 1}
    traverse_impl(instance, state, cw_impl)
    # TODO: Make below declaration safer
    cw_impl.add_line(
        "uint8_t avlos_get_hash(uint8_t * buffer, uint8_t * buffer_len, bool rtr) {{ const uint32_t v = {}; memcpy(buffer, &v, sizeof(v)); return CANRP_Read; }}".format(
            instance.hash_string
        )
    )

    # Write out
    with open(config["paths"]["output_impl"], "w") as output_file:
        print(cw_impl, file=output_file)


def traverse_function_list(obj, state, cw):
    try:
        for child in obj.children.values():
            traverse_function_list(child, state, cw)
    except AttributeError:
        f_name = get_f_name(obj.c_getter)
        state["f_list"].append(
            AddressOf(Variable(f_name, FuncPtr("uint8_t", arguments=get_args())))
        )


def output_function_array(f_list, cw):
    v = Variable("avlos_funcs", FuncPtr("uint8_t", arguments=get_args()), value=f_list)
    cw.add_variable_initialization(v)


def traverse_header(obj, state, cw):
    try:
        for child in obj.children.values():
            traverse_header(child, state, cw)
    except AttributeError:
        f_name = get_f_name(obj.c_getter)
        cw.start_comment()
        cw.add_line(f_name)
        cw.add_line("")
        cw.add_line(obj.description)
        cw.add_line("")
        cw.add_line("@param buffer")
        cw.add_line("@param buffer_len")
        cw.add_line("@param rtr")
        cw.end_comment()
        fun = Function(f_name, "uint8_t", arguments=get_args())
        cw.add_function_prototype(fun)
        cw.add_line("")


def traverse_impl(obj, state, cw):
    try:
        for child in obj.children.values():
            traverse_impl(child, state, cw)
    except AttributeError:
        fun = Function("avlos_{}".format(obj.c_getter), "uint8_t", arguments=get_args())
        fun.codewriter = CodeWriter()
        v = Variable("v", c_type_map[obj.dtype])
        fun.codewriter.add_variable_declaration(v)
        fun.add_code("v = {}();".format(obj.c_getter))
        fun.add_code("*buffer_len = sizeof({});".format(c_type_map[obj.dtype]))
        fun.add_code("memcpy(buffer, &v, sizeof({}));".format(c_type_map[obj.dtype]))
        fun.add_code("return CANRP_Read;")
        cw.add_function_definition(fun)
        cw.add_line("")

        c_setter = None
        try:
            c_setter = obj.c_setter
        except AttributeError:
            pass
        if c_setter:
            s_arg1 = Variable("buffer", "uint8_t *")
            s_arg2 = Variable("buffer_len", "uint8_t *")
            s_arg3 = Variable("rtr", "bool")
            fun = Function(
                "avlos_{}".format(c_setter),
                "uint8_t",
                arguments=(s_arg1, s_arg2, s_arg3),
            )
            fun.codewriter = CodeWriter()
            v = Variable("v", c_type_map[obj.dtype])
            fun.codewriter.add_variable_declaration(v)
            fun.add_code(
                "memcpy(&v, buffer, sizeof({}));".format(c_type_map[obj.dtype])
            )
            fun.add_code("{}(v);".format(c_setter))
            fun.add_code("return CANRP_Write;")
            cw.add_function_definition(fun)
            cw.add_line("")


def get_f_name(accessor):
    return "avlos_{}".format(accessor)


def get_args():
    arg1 = Variable("buffer", "uint8_t *")
    arg2 = Variable("buffer_len", "uint8_t *")
    arg3 = Variable("rtr", "bool")
    return arg1, arg2, arg3
