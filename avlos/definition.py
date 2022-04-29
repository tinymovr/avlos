from collections import OrderedDict
from marshmallow import Schema, fields, post_load, validate
from avlos.unit_field import UnitField
from pprint import pformat

unit_strings = ["bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "float"]


class RemoteNode:
    def __init__(self, remote_attributes, name, description=None):
        self.name = name
        self.description = description
        od = OrderedDict()
        for attrib in remote_attributes:
            od[attrib.name] = attrib
        self.remote_attributes = od

    def str_dump(self, indent, depth):
        if depth <= 0:
            return "..."
        lines = []
        for key, val in self.remote_attributes.items():
            if isinstance(val, RemoteNode):
                val_str = (
                    indent
                    + key
                    + (": " if depth == 1 else ":\n")
                    + val.str_dump(indent + "  ", depth - 1)
                )
            else:
                val_str = indent + val.str_dump()
            lines.append(val_str)
        return "\n".join(lines)

    def __str__(self):
        return self.str_dump("", depth=2)

    def __repr__(self):
        return self.__str__()


class RemoteEndpoint:
    def __init__(
        self,
        name,
        description,
        dtype,
        c_getter,
        unit=None,
        c_setter=None,
        rst_target=None,
        ep_id=-1,
    ):
        self.name = name
        self.description = description
        self.dtype = dtype
        self.unit = unit
        self.c_getter = c_getter
        self.c_setter = c_setter
        self.rst_target = rst_target
        self.ep_id = ep_id

    def str_dump(self):
        return "{} ({}): {}".format(
            self.name, self.dtype, 10 * self.unit if self.unit else 10
        )


class RemoteNodeSchema(Schema):
    name = fields.String(
        required=True, error_messages={"required": "Name is required."}
    )
    description = fields.String()
    remote_attributes = fields.List(fields.Nested(lambda: RemoteNodeSchema()))
    dtype = fields.String(validate=validate.OneOf(unit_strings))
    unit = UnitField()
    c_getter = fields.String()
    c_setter = fields.String()
    rst_target = fields.String()
    ep_id = fields.Integer(default=-1)

    def __init__(self, *args, **kwargs):
        self.idx = 0
        super().__init__(*args, **kwargs)

    @post_load
    def make_remote_node(self, data, **kwargs):
        if "remote_attributes" in data:
            return RemoteNode(**data)
        data["ep_id"] = self.idx
        self.idx += 1
        return RemoteEndpoint(**data)
