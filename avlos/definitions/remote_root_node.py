from functools import cached_property
from marshmallow import fields, post_load
from avlos.definitions import RemoteNode, RemoteNodeSchema


class RootNode(RemoteNode):
    """
    Remote root node with a few additional attributes
    """

    def __init__(self, version, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = version

    @cached_property
    def root(self):
        return self


class RootNodeSchema(RemoteNodeSchema):
    """
    Custom Marshmallow schema for the root node
    """

    version = fields.String()

    @post_load
    def make_remote_node(self, data, **kwargs):
        if "remote_attributes" in data:
            node = RootNode(**data)
            for child in node.remote_attributes.values():
                child._parent = node
            return node
