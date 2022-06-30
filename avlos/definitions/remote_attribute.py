import pint
from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode


class RemoteAttribute(CommNode, NamedNode):
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
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
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
        try:
            __value = __value.to(self.unit).magnitude
        except AttributeError:
            pass
        print(__value)
        data = self.channel.serializer.serialize([__value], self.dtype)
        self.channel.send(data, self.ep_id)

    def str_dump(self):
        return "{0} [{1}]: {2:.6g}".format(
            self.name,
            self.dtype.nickname,
            self.get_value(),
        )

