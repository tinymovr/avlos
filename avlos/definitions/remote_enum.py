from avlos.mixins.comm_node import CommNode
from avlos.mixins.named_node import NamedNode
from avlos.mixins.meta_node import MetaNode
from avlos.mixins.impex_node import ImpexNode
from avlos.datatypes import DataType
from avlos.mixins.func_attr_node import FuncAttrNode


class RemoteEnum(CommNode, NamedNode, MetaNode, ImpexNode):
    """
    Remote Endpoint with a value represented as an enum
    """

    enum_type = DataType.UINT8

    def __init__(
        self,
        name,
        summary,
        func_attr=None,
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
        FuncAttrNode.__init__(self, func_attr)
        self.summary = summary
        self.options = options  # options is needed to deserialize
        self.getter_name = getter_name
        self.setter_name = setter_name
        self.export = export
        self.rst_target = rst_target
        self.ep_id = ep_id

    def get_value(self):
        """
        Retrieve the current enum value from the remote endpoint.
        Sends a request, receives the raw integer value, and converts it to the corresponding enum member.

        Returns:
            The enum member corresponding to the remote value
        """
        assert self.getter_name
        self.channel.send([], self.ep_id)
        data = self.channel.recv(self.ep_id)
        value, *_ = self.channel.serializer.deserialize(data, self.enum_type)
        return self.options(value)

    def set_value(self, __value):
        """
        Set a new enum value on the remote endpoint.
        Accepts values as integers, enum members, or string names, and converts them appropriately.

        Args:
            __value: The value to set (int, enum member, or string name)

        Raises:
            ValueError: If the value cannot be converted to a valid enum member
        """
        assert self.setter_name
        # Check if the value is already an integer and within the range of the enum
        if isinstance(__value, int) and __value in self.options._value2member_map_:
            value = __value

        # Check if the value is a member of the enum
        elif isinstance(__value, self.options):
            value = __value.value

        # Check if the value is a string corresponding to an enum member
        elif isinstance(__value, str) and __value in self.options._member_map_:
            value = self.options[__value].value

        else:
            raise ValueError(
                f"Invalid value: {__value}. Expected an integer, an enum member, or a string corresponding to an enum member."
            )
        data = self.channel.serializer.serialize([value], self.dtype)
        self.channel.send(data, self.ep_id)

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
        """
        Generate a formatted string representation of the enum attribute and its current value.

        Returns:
            A formatted string showing the attribute name and current enum member
        """
        val = self.get_value()
        return "{0}: {1}".format(self.name, str(val))
