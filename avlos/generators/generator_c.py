
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
    cw = CodeWriter()
    cw.add_autogen_comment()
    cw.add_line("")
    try:
        for header in config["c_includes"]:
            cw.include(header)
        cw.add_line("")
    except AttributeError:
        pass
    state = {"ep_counter": 1}
    traverse(instance, state, cw)
    with open(config["output_file"], "w") as output_file:
        print(cw, file=output_file)
    

def traverse(obj, state, cw):
    try:
        for child in obj.children.values():
            traverse(child, state, cw)
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
        

    # cw.add_variable_initialization(var)



# uint8_t CAN_SetCANConfig(uint8_t buffer[], uint8_t *buffer_len, bool rtr)
# {
#     uint8_t id;
#     uint16_t baudrate;
#     memcpy(&id, &buffer[0], sizeof(uint8_t));
#     memcpy(&baudrate, &buffer[1], sizeof(uint16_t));
#     CAN_ResponseType response = CANRP_NoAction;
#     if (id >= 1u)
#     {
#         CAN_set_ID(id);
#         response = CANRP_Write;
#     }
#     if ((baudrate >= 50u) && (baudrate <= 1000u))
#     {
#         CAN_set_kbit_rate(baudrate);
#         response = CANRP_Write;
#     }
#     return response;
# }