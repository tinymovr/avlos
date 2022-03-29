
from marshmallow import Schema, fields
from avlos.unit_field import UnitField


class NamedSchema(Schema):
    '''
    Abstract Schema subclass with name and initializer
    '''
    name = fields.String(required=True, error_messages={"required": "Name is required."})

    @post_load
    def make_node(self, data, **kwargs) -> TreeNode:
        return type(self).model_class(**data)


class RemoteSystem(NamedSchema):
    '''
    Class representing an instance of a Remote System comprising
    a tree of nodes with endpoints
    '''
    description = fields.String()
    ns = fields.String()
    system_id = fields.Integer(required=True, error_messages={"required": "System ID is required."})
    root = RemoteNode()


class RemoteNode(NamedSchema):
    description = fields.String()
    children = fields.List(fields.Nested(lambda: RemoteNode()))


class RemoteEndpoint(NamedSchema):
    ep_id = fields.Integer(required=True, error_messages={"required": "Endpoint ID is required."})
    unit = UnitField()


class FastRemoteEndpoint(NamedSchema):
    ep_id = fields.Integer(required=True, error_messages={"required": "Endpoint ID is required."})
    endpoints = fields.List(fields.Nested(lambda: RemoteEndpoint()))
    