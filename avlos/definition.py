from collections import OrderedDict
from marshmallow import (
    Schema,
    fields,
    post_load,
    validate,
    validates_schema,
    ValidationError,
)
from avlos.unit_field import UnitField
from avlos.counter import get_counter

unit_strings = ["bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "float"]


class RemoteNode:
    def __init__(self, remote_attributes, name, description=None):
        od = OrderedDict()
        for attrib in remote_attributes:
            od[attrib.name] = attrib
        super().__setattr__("remote_attributes", od)
        self.name = name
        self.description = description

    def __getattr__(self, __name):
        try:
            attr = self.remote_attributes[__name]
            if isinstance(attr, RemoteNode):
                return attr
            elif isinstance(attr, RemoteEndpoint):
                return attr.get_value()
        except KeyError:
            return super().__getattr__(__name)

    def __setattr__(self, __name, __value):
        try:
            attr = self.remote_attributes[__name]
            if isinstance(attr, RemoteEndpoint):
                return attr.set_value(__value)
        except KeyError:
            super().__setattr__(__name, __value)

    def set_getter_cb(self, cb):
        for attr in self.remote_attributes.values():
            if isinstance(attr, RemoteNode):
                attr.set_getter_cb(cb)
            elif isinstance(attr, RemoteEndpoint):
                attr.getter_cb = cb

    def set_setter_cb(self, cb):
        for attr in self.remote_attributes.values():
            if isinstance(attr, RemoteNode):
                attr.set_setter_cb(cb)
            elif isinstance(attr, RemoteEndpoint):
                attr.setter_cb = cb

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
        c_getter=None,
        c_setter=None,
        unit=None,
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

        self.getter_cb = None
        self.setter_cb = None

    def get_value(self):
        return self.getter_cb(self.ep_id)

    def set_value(self, __value):
        self.setter_cb(self.ep_id, __value)

    def str_dump(self):
        return "{}. {} ({}): {}".format(
            self.ep_id,
            self.name,
            self.dtype,
            self.get_value() * self.unit if self.unit else self.get_value(),
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
        self.counter = get_counter()
        super().__init__(*args, **kwargs)

    @post_load
    def make_remote_node(self, data, **kwargs):
        if "remote_attributes" in data:
            return RemoteNode(**data)
        data["ep_id"] = self.counter.next()
        return RemoteEndpoint(**data)

    @validates_schema
    def validate_getter_setter(self, data, **kwargs):
        if (
            "remote_attributes" not in data
            and "c_getter" not in data
            and "c_setter" not in data
        ):
            raise ValidationError(
                "Either a getter, setter or remote attributes list is required"
            )
