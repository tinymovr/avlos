
import json
import hashlib
from avlos.definition import RemoteNodeSchema


def deserialize(system_description):
    system_schema = RemoteNodeSchema()
    system_obj = system_schema.load(system_description)
    system_obj.hash_string = hash_string_from_string(json.dumps(system_description))
    return system_obj


def hash_string_from_string(input_string):
    return hex(int.from_bytes(hashlib.sha256(input_string.encode()).digest()[:4], 'little'))