import os
import avlos
from csnake import CodeWriter, Function, Variable, FormattedLiteral


c_type_map = {
    "bool": "bool",
    "int8": "int8_t",
    "uint8": "uint8_t",
    "int16": "int16_t",
    "uint16": "uint16_t",
    "int32": "int32_t",
    "uint32": "uint32_t",
    "float": "float"
}


def process(instance, config):
    # Header
    cw_head = CodeWriter()
    cw_head.add_autogen_comment()
    cw_head.add_line("")
    try:
        for header in config["c_includes"]:
            cw_head.include(header)
        cw_head.add_line("")
    except KeyError:
        pass
    state = {"ep_counter": 1}
    traverse_header(instance, state, cw_head)
    with open(config["paths"]["output_header"], "w") as output_file:
        print(cw_head, file=output_file)

    # Implementation
    cw_impl = CodeWriter()
    cw_impl.add_autogen_comment()
    cw_impl.add_line("")
    cw_impl.include(output_file.name)
    cw_impl.add_line("")
    state = {"ep_counter": 1}
    traverse_impl(instance, state, cw_impl)
    with open(config["paths"]["output_impl"], "w") as output_file:
        print(cw_impl, file=output_file)


def traverse_header(obj, state, cw):
    try:
        for child in obj.children.values():
            traverse_header(child, state, cw)
    except AttributeError:
        f_name = "avlos_{}".format(obj.c_getter)
        cw.start_comment()
        cw.add_line(f_name)
        cw.add_line("")
        cw.add_line(obj.description)
        cw.add_line("")
        cw.add_line("@param buffer")
        cw.add_line("@param buffer_len")
        cw.add_line("@param rtr")
        cw.end_comment()
        arg1 = Variable("buffer", "uint8_t *")
        arg2 = Variable("buffer_len", "uint8_t *")
        arg3 = Variable("rtr", "bool")
        fun = Function( f_name, "uint8_t", arguments=(arg1, arg2, arg3))
        cw.add_function_prototype(fun)
        cw.add_line("") 


def traverse_impl(obj, state, cw):
    try:
        for child in obj.children.values():
            traverse_impl(child, state, cw)
    except AttributeError:
        arg1 = Variable("buffer", "uint8_t *")
        arg2 = Variable("buffer_len", "uint8_t *")
        arg3 = Variable("rtr", "bool")
        fun = Function(
            "avlos_{}".format(obj.c_getter),
            "uint8_t",
            arguments=(arg1, arg2, arg3)
        )
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
                arguments=(s_arg1, s_arg2,s_arg3)
            )
            fun.codewriter = CodeWriter()
            v = Variable("v", c_type_map[obj.dtype])
            fun.codewriter.add_variable_declaration(v)
            fun.add_code("memcpy(&v, buffer, sizeof({}));".format(c_type_map[obj.dtype]))
            fun.add_code("{}(v);".format(c_setter))
            fun.add_code("return CANRP_Write;")
            cw.add_function_definition(fun)
            cw.add_line("")
