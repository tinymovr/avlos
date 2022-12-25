from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode
from avlos.mixins.meta_node import MetaNode
from avlos.mixins.impex_node import ImpexNode
from avlos.datatypes import DataType


class RemoteEnum(CommNode, NamedNode, MetaNode, ImpexNode):
    """
    Remote Endpoint with a value represented as an enum
    """

    enum_type = DataType.UINT8

    def __init__(
        self,
        name,
        summary,
        getter_name=None,
        setter_name=None,
        options=None,
        rst_target=None,
        export=False,
        ep_id=-1,
        meta={},
    ):
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
        MetaNode.__init__(self, meta_dict=meta)
        self.summary = summary
        self.options = options  # options is needed to deserialize
        self.getter_name = getter_name
        self.setter_name = setter_name
        self.export = export
        self.rst_target = rst_target
        self.ep_id = ep_id

    def get_value(self):
        assert self.getter_name
        self.channel.send([], self.ep_id)
        data = self.channel.recv(self.ep_id)
        value, *_ = self.channel.serializer.deserialize(data, self.enum_type)
        return self.options(value)

    def set_value(self, __value):
        raise NotImplementedError

    def export_options(self, namespace):
        """
        Export the members of the enum to the
        indicated namespace
        """
        if self.export:
            namespace.update(self.options.__members__)

    @property
    def dtype(self):
        """
        Mocks the endpoint datatype
        """
        return self.enum_type

    @property
    def unit(self):
        """
        Mocks the endpoint unit
        """
        return None

    def str_dump(self):
        val = self.get_value()
        return "{0}: {1}".format(self.name, str(val))
