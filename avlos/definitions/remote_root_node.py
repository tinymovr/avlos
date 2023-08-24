from functools import cached_property
from marshmallow import fields, post_load
from avlos.definitions import RemoteNode, RemoteNodeSchema


class RootNode(RemoteNode):
    """
    Represent a remote root node with additional attributes.
    Extend from the RemoteNode class.
    """

    def __init__(self, version=None, *args, **kwargs):
        """
        Initialize a new instance of the RootNode.

        Args:
            version (str, optional): Version of the root node. Deprecated, defaults to None.
            *args: Variable length argument list to be passed to the superclass.
            **kwargs: Arbitrary keyword arguments to be passed to the superclass.
        """
        super().__init__(*args, **kwargs)

    @cached_property
    def root(self):
        """
        Cached property that returns the root node itself.

        Returns:
            RootNode: Self instance representing the root node.
        """
        return self


class RootNodeSchema(RemoteNodeSchema):
    """
    Custom Marshmallow schema for the root node
    """

    # The version field is deprecated since 0.6.0, but maintained
    # here to avoid breaking specs
    version = fields.Str()

    @post_load
    def make_remote_node(self, data, **kwargs):
        if "remote_attributes" in data:
            node = RootNode(**data)
            for child in node.remote_attributes.values():
                child._parent = node
            return node
