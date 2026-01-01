from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode
from avlos.mixins.meta_node import MetaNode
from avlos.mixins.impex_node import ImpexNode
from avlos.datatypes import DataType
from avlos.mixins.func_attr_node import FuncAttrNode


class RemoteBitmask(CommNode, NamedNode, MetaNode, ImpexNode):
    """
    Remote Endpoint with a value represented as a bitmask
    """

    flag_type = DataType.UINT8

    def __init__(
        self,
        name,
        summary,
        func_attr=None,
        getter_name=None,
        setter_name=None,
        flags=None,
        rst_target=None,
        export=False,
        ep_id=-1,
        meta={},
    ):
        CommNode.__init__(self)
        NamedNode.__init__(self, name)
        MetaNode.__init__(self, meta_dict=meta)
        FuncAttrNode.__init__(self, func_attr)
        self.summary = summary
        self.bitmask = flags  # flags is needed to deserialize
        self.getter_name = getter_name
        self.setter_name = setter_name
        self.export = export
        self.rst_target = rst_target
        self.ep_id = ep_id

    def get_value(self):
        """
        Retrieve the current bitmask value from the remote endpoint.
        Sends a request, receives the raw integer value, and converts it to a bitmask object.

        Returns:
            The bitmask object representing the active flags
        """
        assert self.getter_name
        self.channel.send([], self.ep_id)
        data = self.channel.recv(self.ep_id)
        value, *_ = self.channel.serializer.deserialize(data, self.flag_type)
        return self.bitmask(value)

    def set_value(self, __value):
        """
        Setting bitmask values is not currently supported.

        Raises:
            NotImplementedError: Always raised as this operation is not implemented
        """
        raise NotImplementedError

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
        """
        Generate a formatted string representation of the bitmask attribute and its current value.

        Returns:
            A formatted string showing the attribute name and active flags, or indication of no flags
        """
        val = self.get_value()
        return "{0}: {1}".format(
            self.name,
            str(val) if val > 0 else "(no flags)",
        )
