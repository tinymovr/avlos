
from marshmallow import Schema, fields, post_load, validate
from avlos.unit_field import UnitField
from pprint import pformat

unit_strings = ["bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "float"]


class RemoteNode:

    def __init__(self, children, name, description=None):
        self.name = name
        self.description = description
        self.children = {c.name: c for c in children}

    def str_dump(self, indent, depth):
        if depth <= 0:
            return "..."
        lines = []
        for key, val in self.children.items():
            if isinstance(val, RemoteNode):
                val_str = indent + key + (": " if depth == 1 else ":\n") + val.str_dump(indent + "  ", depth - 1)
            else:
                val_str = indent + val.str_dump()
            lines.append(val_str)
        return "\n".join(lines)

    def __str__(self):
        return self.str_dump("", depth=2)

    def __repr__(self):
        return self.__str__()


class RemoteEndpoint:

    def __init__(self, name, description, dtype, c_getter, unit=None, c_setter=None):
        self.name = name
        self.description = description
        self.dtype = dtype
        self.unit = unit
        self.c_getter = c_getter
        self.c_setter = c_setter

    def str_dump(self):
        return "{} ({}): {}".format(self.name, self.dtype, 10*self.unit if self.unit else 10)


class RemoteNodeSchema(Schema):
    name = fields.String(required=True, error_messages={"required": "Name is required."})
    description = fields.String()
    children = fields.List(fields.Nested(lambda: RemoteNodeSchema()))
    dtype = fields.String(validate=validate.OneOf(unit_strings))
    unit = UnitField()
    c_getter = fields.String()
    c_setter = fields.String()

    @post_load
    def make_remote_node(self, data, **kwargs):
        if 'children' in data:
            return RemoteNode(**data)
        return RemoteEndpoint(**data)
