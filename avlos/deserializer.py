
from avlos.definition import RemoteNodeSchema

def deserialize(system_description):
    system_schema = RemoteNodeSchema()
    system_obj = system_schema.load(system_description)
    return system_obj