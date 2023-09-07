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
from avlos.enum_field import EnumField
from avlos.counter import get_counter
from avlos.datatypes import DataTypeField
from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode
from avlos.mixins.impex_node import ImpexNode
from avlos.definitions import (
    RemoteAttribute,
    RemoteFunction,
    RemoteArgumentSchema,
    RemoteBitmask,
    RemoteEnum,
)


class RemoteNode(CommNode, NamedNode, ImpexNode):
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
            try:
                return attr.get_value()
            except AttributeError:
                return attr
        except KeyError:
            raise AttributeError(__name)

    def __setattr__(self, __name, __value):
        try:
            attr = self.remote_attributes[__name]
            return attr.set_value(__value)
        except KeyError:
            super().__setattr__(__name, __value)

    def export_flags(self, namespace):
        """
        Recurse children and export bitmask to
        indicated namespace
        """
        for child in self.remote_attributes:
            try:
                child.export_flags(namespace)
            except AttributeError:
                pass

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
    options = EnumField()
    unit = UnitField()
    func_attr = fields.String(default=None)
    getter_name = fields.String()
    setter_name = fields.String()
    caller_name = fields.String()
    arguments = fields.List(fields.Nested(lambda: RemoteArgumentSchema()))
    export = fields.Bool(default=False)
    rst_target = fields.String()
    ep_id = fields.Integer(default=-1)
    meta = fields.Dict(default={})

    def __init__(self, *args, **kwargs):
        self.counter = get_counter()
        super().__init__(*args, **kwargs)

    @post_load
    def make_remote_node(self, data, **kwargs):
        """
        Decide on which type of object to instantiate
        based on the initialization data available.
        Overrides the post_load hook.
        """
        if "remote_attributes" in data:
            node = RemoteNode(**data)
            for child in node.remote_attributes.values():
                child._parent = node
            return node
        elif "caller_name" in data:
            data["ep_id"] = self.counter.next()
            return RemoteFunction(**data)
        elif "dtype" in data:
            data["ep_id"] = self.counter.next()
            return RemoteAttribute(**data)
        elif "flags" in data:
            data["ep_id"] = self.counter.next()
            return RemoteBitmask(**data)
        elif "options" in data:
            data["ep_id"] = self.counter.next()
            return RemoteEnum(**data)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if (
            "remote_attributes" not in data
            and "getter_name" not in data
            and "setter_name" not in data
            and "caller_name" not in data
        ):
            raise ValidationError(
                "Either a getter, setter, caller or remote attributes list is required"
            )
        if "getter_name" in data and "setter_name" in data and "caller_name" in data:
            raise ValidationError(
                "A getter, setter, and caller cannot coexist in a single endpoint"
            )
        if (
            ("getter_name" in data or "setter_name" in data or "caller_name" in data)
            and "dtype" not in data
            and "flags" not in data
            and "options" not in data
        ):
            raise ValidationError("Data type, flags or options field is required")
