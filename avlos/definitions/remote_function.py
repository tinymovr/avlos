from marshmallow import (
    Schema,
    fields,
    post_load,
)
from avlos.unit_field import UnitField
from avlos.datatypes import DataTypeField
from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode


class RemoteFunction(CommNode, NamedNode):
    """
    Remote Function with zero or more arguments, return
    type, parent and a comms channel
    """

    def __init__(
        self,
        name,
        summary,
        caller_name,
        arguments,
        dtype=None,
        unit=None,
        rst_target=None,
        ep_id=-1,
    ):
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
        self.summary = summary
        self.dtype = dtype
        self.unit = unit
        self.caller_name = caller_name
        self.arguments = arguments
        self.rst_target = rst_target
        self.ep_id = ep_id

    def __call__(self, *args):
        data = self.channel.serializer.serialize(
            args, *[arg.dtype for arg in self.arguments]
        )
        self.channel.send(data, self.ep_id)
        if not self.dtype.is_void:
            data = self.channel.recv(self.ep_id)
            value, *_ = self.channel.serializer.deserialize(data, self.dtype)
            try:
                return value * self.unit
            except TypeError:
                pass
            return value

    def str_dump(self):
        return "{}({}) -> {}".format(
            self.name,
            ", ".join([arg.as_function_argument for arg in self.arguments]),
            self.dtype.nickname,
        )


class RemoteArgument:
    """
    Class representing a RemoteFunction argument
    """

    def __init__(self, name, dtype, unit=None, summary=None):
        self.name = name
        self.dtype = dtype
        self.unit = unit
        self.summary = summary

    @property
    def as_function_argument(self):
        return " ".join([self.dtype.nickname, self.name])


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
