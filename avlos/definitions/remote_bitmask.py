from avlos.mixins.comm_node import CommNode
from avlos.datatypes import DataType


class RemoteBitmask(CommNode):
    """
    Remote Endpoint with a value represented as a bitmask
    """

    flag_type = DataType.UINT8

    def __init__(
        self,
        name,
        summary,
        c_getter=None,
        c_setter=None,
        flags=None,
        rst_target=None,
        ep_id=-1,
    ):
        super().__init__()
        self.name = name
        self.summary = summary
        self.flags = flags
        self.c_getter = c_getter
        self.c_setter = c_setter
        self.rst_target = rst_target
        self.ep_id = ep_id

    def get_value(self):
        assert self.c_getter
        self.channel.send([], self.ep_id)
        data = self.channel.recv(self.ep_id)
        value, *_ = self.channel.serializer.deserialize(data, self.flag_type)
        return self.flags.match(value)

    def set_value(self, __value):
        assert self.c_setter
        data = self.channel.serializer.serialize(
            [self.flags.mask(__value)], self.flag_type
        )
        self.channel.send(data, self.ep_id)

    @property
    def dtype(self):
        """
        Mocks the endpoint datatype
        """
        return self.flag_type

    @property
    def unit(self):
        """
        Mocks the endpoint unit
        """
        return None

    def str_dump(self):
        val = self.get_value()
        return "{0}: {1}".format(
            self.name,
            " ".join(val) if len(val) > 0 else "(no flags)",
        )
