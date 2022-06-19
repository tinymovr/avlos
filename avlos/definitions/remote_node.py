from collections import OrderedDict
from marshmallow import (
    Schema,
    fields,
    post_load,
    validates_schema,
    ValidationError,
)
from avlos.unit_field import UnitField
from avlos.bitmask_field import BitmaskField
from avlos.counter import get_counter
from avlos.datatypes import DataTypeField
from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode
from avlos.definitions import (
    RemoteAttribute,
    RemoteFunction,
    RemoteArgumentSchema,
    RemoteBitmask,
)


class RemoteNode(CommNode, NamedNode):
    """
    Remote node with parent, children and a comms channel
    """

    def __init__(self, remote_attributes, name, summary=None):
        od = OrderedDict()
        for attrib in remote_attributes:
            od[attrib.name] = attrib
        super().__setattr__("remote_attributes", od)
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
        self.summary = summary

    def __getattr__(self, __name):
        try:
            attr = self.remote_attributes[__name]
            if isinstance(attr, RemoteNode) or isinstance(attr, RemoteFunction):
                return attr
            elif isinstance(attr, RemoteAttribute):
                return attr.get_value()
        except KeyError:
            raise AttributeError(__name)

    def __setattr__(self, __name, __value):
        try:
            attr = self.remote_attributes[__name]
            if isinstance(attr, RemoteAttribute):
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

    def __dir__(self):
        return self.remote_attributes.keys()


class RemoteNodeSchema(Schema):
    """
    Custom Marshmallow schema for generating RemoteNode,
    RemoteAttribute, RemoteBitmask and RemoteFunction classes
    """

    name = fields.String(
        required=True, error_messages={"required": "Name is required."}
    )
    summary = fields.String()
    remote_attributes = fields.List(fields.Nested(lambda: RemoteNodeSchema()))
    dtype = DataTypeField()
    flags = BitmaskField()
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
        elif "dtype" in data:
            data["ep_id"] = self.counter.next()
            return RemoteAttribute(**data)
        elif "flags" in data:
            data["ep_id"] = self.counter.next()
            return RemoteBitmask(**data)

    @validates_schema
    def validate_schema(self, data, **kwargs):
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
        if (
            ("c_getter" in data or "c_setter" in data or "c_caller" in data)
            and "dtype" not in data
            and "flags" not in data
        ):
            raise ValidationError("Data type or flags field is required")
