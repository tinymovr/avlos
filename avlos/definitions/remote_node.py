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
        """
        Initialize a remote node with attributes organized as an ordered dictionary.

        Args:
            remote_attributes: List of remote attributes/functions/nodes to be accessed by name
            name: The name identifier for this node
            summary: Optional description of the node's purpose
        """
        od = OrderedDict()
        for attrib in remote_attributes:
            od[attrib.name] = attrib
        super().__setattr__("remote_attributes", od)
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
        self.summary = summary

    def __getattr__(self, __name):
        """
        Enable dynamic attribute access for remote attributes.
        Attempts to call get_value() if the attribute supports it, otherwise returns the attribute itself.

        Args:
            __name: Name of the attribute to access

        Returns:
            The value of the remote attribute, or the attribute object itself

        Raises:
            AttributeError: If the attribute name doesn't exist in remote_attributes
        """
        try:
            attr = self.remote_attributes[__name]
            try:
                return attr.get_value()
            except AttributeError:
                return attr
        except KeyError:
            raise AttributeError(__name)

    def __setattr__(self, __name, __value):
        """
        Enable dynamic attribute setting for remote attributes.
        Delegates to the attribute's set_value() method if it's a remote attribute,
        otherwise falls back to standard attribute setting.

        Args:
            __name: Name of the attribute to set
            __value: Value to set the attribute to
        """
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
        """
        Generate a formatted string representation of the node and its children.
        Recursively traverses child nodes up to the specified depth.

        Args:
            indent: String used for indentation at the current level
            depth: Maximum recursion depth for displaying nested nodes

        Returns:
            Formatted multi-line string representation of the node hierarchy
        """
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
    func_attr = fields.String(dump_default=None)
    getter_name = fields.String()
    setter_name = fields.String()
    caller_name = fields.String()
    arguments = fields.List(fields.Nested(lambda: RemoteArgumentSchema()))
    export = fields.Bool(dump_default=False)
    rst_target = fields.String()
    ep_id = fields.Integer(dump_default=-1)
    meta = fields.Dict(dump_default={})

    def __init__(self, *args, **kwargs):
        """
        Initialize the schema with a counter for assigning unique endpoint IDs.
        """
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
        """
        Validate that the schema data meets structural requirements.
        Ensures nodes have either child attributes or endpoint functionality,
        and that endpoints have appropriate data type definitions.

        Raises:
            ValidationError: If validation rules are violated
        """
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
