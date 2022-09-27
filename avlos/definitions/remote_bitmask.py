from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode
from avlos.datatypes import DataType


class RemoteBitmask(CommNode, NamedNode):
    """
    Remote Endpoint with a value represented as a bitmask
    """

    flag_type = DataType.UINT8

    def __init__(
        self,
        name,
        summary,
        getter_name=None,
        setter_name=None,
        flags=None,
        rst_target=None,
        export=False,
        ep_id=-1,
        dynamic_value=False,
    ):
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
        self.summary = summary
        self.bitmask = flags  # flags is needed to deserialize
        self.getter_name = getter_name
        self.setter_name = setter_name
        self.export = export
        self.rst_target = rst_target
        self.ep_id = ep_id
        self.dynamic_value = dynamic_value

    def get_value(self):
        assert self.getter_name
        self.channel.send([], self.ep_id)
        data = self.channel.recv(self.ep_id)
        value, *_ = self.channel.serializer.deserialize(data, self.flag_type)
        return self.bitmask(value)

    def set_value(self, __value):
        raise NotImplementedError
        # assert self.setter_name
        # data = self.channel.serializer.serialize(
        #     [self.bitmask.mask(__value)], self.flag_type
        # )
        # self.channel.send(data, self.ep_id)

    def export_flags(self, namespace):
        """
        Export the members of the bitmask to the
        indicated namespace
        """
        if self.export:
            namespace.update(self.bitmask.__members__)

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
            str(val) if val > 0 else "(no flags)",
        )
