import os
import avlos
from csnake import (
    CodeWriter,
    Enum,
    Function,
    FuncPtr,
    Variable,
    AddressOf,
    FormattedLiteral,
)


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
    cw_head.add_line("#pragma once")
    cw_head.add_line("")

    # Imports
    try:
        for header in config["c_includes"]:
            cw_head.include(header)
        cw_head.add_line("")
    except KeyError:
        pass

    # Function prototypes
    # TODO: Make below declaration safer
    cw_head.add_line("uint8_t avlos_get_hash(uint8_t * buffer, uint8_t * buffer_len);")
    cw_head.add_line("")
    state = {"ep_counter": 1, "prefix": ""}
    traverse_header(instance, state, cw_head)

    # Function list
    state = {
        "f_list": [
            AddressOf(
                Variable("avlos_get_hash", FuncPtr("uint8_t", arguments=get_args()))
            )
        ]
    }
    traverse_function_list(instance, state, cw_head)
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

    # Enums
    enum_dir = Enum("Avlos_Directive", prefix="AVLOS_DIR_", typedef=True)
    enum_dir.add_value("READ", 0)
    enum_dir.add_value("WRITE", 1)
    cw_impl.add_enum(enum_dir)
    cw_impl.add_line("")

    enum_ret = Enum("Avlos_Return", prefix="AVLOS_RET_", typedef=True)
    enum_ret.add_value("NOACTION", 0)
    enum_ret.add_value("READ", 1)
    enum_ret.add_value("WRITE", 2)
    cw_impl.add_enum(enum_ret)
    cw_impl.add_line("")

    # Implementations
    # TODO: Make below declaration safer
    cw_impl.add_line(
        "uint8_t avlos_get_hash(uint8_t * buffer, uint8_t * buffer_len) {{ const uint32_t v = {}; memcpy(buffer, &v, sizeof(v)); return AVLOS_RET_READ; }}".format(
            instance.hash_string
        )
    )
    cw_impl.add_line("")
    state = {"ep_counter": 1, "prefix": ""}
    traverse_impl(instance, state, cw_impl)

    # Write out
    with open(config["paths"]["output_impl"], "w") as output_file:
        print(cw_impl, file=output_file)


def traverse_function_list(obj, state, cw):
    try:
        for child in obj.remote_attributes.values():
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
        current_prefix = state["prefix"]
        for child in obj.remote_attributes.values():
            state["prefix"] = "{}{}_".format(current_prefix, obj.name)
            traverse_header(child, state, cw)
        state["prefix"] = current_prefix
    except AttributeError:
        f_name = get_f_name("{}{}".format(state["prefix"], obj.name))
        cw.start_comment()
        cw.add_line(f_name)
        cw.add_line("")
        cw.add_line(obj.description)
        cw.add_line("")
        cw.add_line("@param buffer")
        cw.add_line("@param buffer_len")
        cw.end_comment()
        fun = Function(f_name, "uint8_t", arguments=get_args())
        cw.add_function_prototype(fun)
        cw.add_line("")


def traverse_impl(obj, state, cw):
    try:
        current_prefix = state["prefix"]
        for child in obj.remote_attributes.values():
            state["prefix"] = "{}{}_".format(current_prefix, obj.name)
            traverse_impl(child, state, cw)
        state["prefix"] = current_prefix
    except AttributeError:
        f_name = get_f_name("{}{}".format(state["prefix"], obj.name))
        fun = Function(f_name, "uint8_t", arguments=get_args())
        fun.codewriter = CodeWriter()
        v = Variable("v", c_type_map[obj.dtype])
        fun.codewriter.add_variable_declaration(v)
        try:
            c_setter = obj.c_setter
        except AttributeError:
            c_setter = None

        # TODO: Make implementation using safe primitives
        fun.codewriter.add_line("if (AVLOS_DIR_READ == buffer[0]) {")
        fun.codewriter.add_line("    v = {}();".format(obj.c_getter))
        fun.codewriter.add_line("    *buffer_len = sizeof(v);")
        fun.codewriter.add_line("    memcpy(buffer+1, &v, sizeof(v));")
        fun.codewriter.add_line("    return AVLOS_RET_READ;")
        fun.codewriter.add_line("}")
        if c_setter:
            fun.codewriter.add_line("else if (AVLOS_DIR_WRITE == buffer[0]) {")
            fun.codewriter.add_line("    memcpy(&v, buffer+1, sizeof(v));")
            fun.codewriter.add_line("    {}(v);".format(c_setter))
            fun.codewriter.add_line("    return AVLOS_RET_WRITE;")
            fun.codewriter.add_line("}")
        fun.codewriter.add_line("return AVLOS_RET_NOACTION;")
        # uint32_t v;
        # if (AVLOS_DIR_READ == buffer[0]) {
        #     *buffer_len = sizeof(v);
        #     memcpy(buffer, &v, sizeof(v));
        #     return AVLOS_RET_READ;
        # }
        # else if (AVLOS_DIR_WRITE == buffer[0]) {
        #     memcpy(&v, buffer, sizeof(v));
        #     motor_set_R(v);
        #     return AVLOS_RET_WRITE;
        # }
        # return AVLOS_RET_NOACTION;

        cw.add_function_definition(fun)
        cw.add_line("")


def get_f_name(accessor):
    return "avlos_{}".format(accessor)


def get_args():
    arg1 = Variable("buffer", "uint8_t *")
    arg2 = Variable("buffer_len", "uint8_t *")
    return arg1, arg2
