from marshmallow import (
    Schema,
    fields,
    post_load,
)
from avlos.unit_field import UnitField
from avlos.datatypes import DataTypeField
from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode
from avlos.mixins.meta_node import MetaNode
from avlos.mixins.func_attr_node import FuncAttrNode


class RemoteFunction(CommNode, NamedNode, MetaNode):
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
        func_attr=None,
        dtype=None,
        unit=None,
        rst_target=None,
        ep_id=-1,
        meta={},
    ):
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
        MetaNode.__init__(self, meta_dict=meta)
        FuncAttrNode.__init__(self, func_attr)
        self.summary = summary
        self.dtype = dtype
        self.unit = unit
        self.caller_name = caller_name
        self.arguments = arguments
        self.rst_target = rst_target
        self.ep_id = ep_id

    def __call__(self, *args):
        mags = []
        for arg_val, arg_obj in zip(args, self.arguments):
            try:
                mags.append(arg_val.to(arg_obj.unit).magnitude)
            except AttributeError:
                mags.append(arg_val)
        data = self.channel.serializer.serialize(
            mags, *[arg.dtype for arg in self.arguments]
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
