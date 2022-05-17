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
from avlos.mixins.comm_node import CommNode
from avlos.datatypes import DataTypeField, datatype_names


class RemoteNode(CommNode):
    """
    Remote node with parent, children and a comms channel
    """

    def __init__(self, remote_attributes, name, summary=None):
        od = OrderedDict()
        for attrib in remote_attributes:
            od[attrib.name] = attrib
        super().__setattr__("remote_attributes", od)
        super().__init__()
        self.name = name
        self.summary = summary

    def __getattr__(self, __name):
        try:
            attr = self.remote_attributes[__name]
            if isinstance(attr, RemoteNode):
                return attr
            elif isinstance(attr, RemoteEndpoint):
                return attr.get_value()
        except KeyError:
            raise AttributeError(__name)

    def __setattr__(self, __name, __value):
        try:
            attr = self.remote_attributes[__name]
            if isinstance(attr, RemoteEndpoint):
                return attr.set_value(__value)
        except KeyError:
            super().__setattr__(__name, __value)

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


class RootNode(RemoteNode):
    """
    Remote root node with a few additional attributes
    """

    def __init__(self, version, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = version


class RemoteEndpoint(CommNode):
    """
    Remote Endpoint with a value, parent and a comms channel
    """

    def __init__(
        self,
        name,
        summary,
        dtype,
        c_getter=None,
        c_setter=None,
        unit=None,
        rst_target=None,
        ep_id=-1,
    ):
        super().__init__()
        self.name = name
        self.summary = summary
        self.dtype = dtype
        self.unit = unit
        self.c_getter = c_getter
        self.c_setter = c_setter
        self.rst_target = rst_target
        self.ep_id = ep_id

    def get_value(self):
        assert self.c_getter
        self.channel.send([], self.ep_id)
        data = self.channel.recv(self.ep_id)
        value, *_ = self.channel.serializer.deserialize(data, self.dtype)
        try:
            return value * self.unit
        except TypeError:
            return value

    def set_value(self, __value):
        assert self.c_setter
        data = self.channel.serializer.serialize([__value], self.dtype)
        self.channel.send(data, self.ep_id)

    def str_dump(self):
        return "{}. {} ({}): {}".format(
            self.ep_id,
            self.name,
            self.dtype,
            self.get_value(),
        )


class RemoteFunction(CommNode):
    """
    Remote Function with zero or more arguments, return
    type, parent and a comms channel
    """

    def __init__(
        self,
        name,
        summary,
        c_caller,
        arguments,
        dtype=None,
        rst_target=None,
        ep_id=-1,
    ):
        super().__init__()
        self.name = name
        self.summary = summary
        self.dtype = dtype
        self.c_caller = c_caller
        self.arguments = arguments
        self.rst_target = rst_target
        self.ep_id = ep_id

    def __call__(self, *args):
        pass

    def str_dump(self):
        return "{}. {}({}) -> {}".format(
            self.ep_id,
            self.name,
            ", ".join(
                [" ".join([arg.dtype.nickname, arg.name]) for arg in self.arguments]
            ),
            self.dtype,
        )


class RemoteArgument:
    """
    Class representing a RemoteFunction argument
    """

    def __init__(self, name, dtype, summary=None):
        self.name = name
        self.dtype = dtype
        self.summary = summary


class RemoteArgumentSchema(Schema):
    """
    Custom Marshmallow schema for generating RemoteFunction
    arguments
    """

    name = fields.String(
        required=True, error_messages={"required": "Name is required."}
    )
    summary = fields.String()
    dtype = DataTypeField(required=True)
    unit = UnitField()

    @post_load
    def make_remote_argument(self, data, **kwargs):
        return RemoteArgument(**data)


class RemoteNodeSchema(Schema):
    """
    Custom Marshmallow schema for generating RemoteNode,
    RemoteEndpoint and RemoteFunction classes
    """

    name = fields.String(
        required=True, error_messages={"required": "Name is required."}
    )
    summary = fields.String()
    remote_attributes = fields.List(fields.Nested(lambda: RemoteNodeSchema()))
    dtype = DataTypeField()
    unit = UnitField()
    c_getter = fields.String()
    c_setter = fields.String()
    c_caller = fields.String()
    arguments = fields.List(fields.Nested(lambda: RemoteArgumentSchema()))
    rst_target = fields.String()
    ep_id = fields.Integer(default=-1)

    def __init__(self, *args, **kwargs):
        self.counter = get_counter()
        super().__init__(*args, **kwargs)

    @post_load
    def make_remote_node(self, data, **kwargs):
        if "remote_attributes" in data:
            node = RemoteNode(**data)
            for child in node.remote_attributes.values():
                child._parent = node
            return node
        elif "c_caller" in data:
            data["ep_id"] = self.counter.next()
            return RemoteFunction(**data)
        else:
            data["ep_id"] = self.counter.next()
            return RemoteEndpoint(**data)

    @validates_schema
    def validate_getter_setter(self, data, **kwargs):
        if (
            "remote_attributes" not in data
            and "c_getter" not in data
            and "c_setter" not in data
            and "c_caller" not in data
        ):
            raise ValidationError(
                "Either a getter, setter, caller or remote attributes list is required"
            )
        if "c_getter" in data and "c_setter" in data and "c_caller" in data:
            raise ValidationError(
                "A getter, setter, and caller cannot coexist in a single endpoint"
            )


class RootNodeSchema(RemoteNodeSchema):
    version = fields.String()

    @post_load
    def make_remote_node(self, data, **kwargs):
        if "remote_attributes" in data:
            node = RootNode(**data)
            for child in node.remote_attributes.values():
                child._parent = node
            return node
