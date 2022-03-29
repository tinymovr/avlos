
from avlos.definition import RemoteSystem, RemoteNode, RemoteEndpoint, FastRemoteEndpoint

def deserialize(data):
    schema = RemoteSystem()
    result = schema.load(data)
    return result