import json
import hashlib
from avlos.definition import RemoteNodeSchema
from avlos.counter import make_counter, get_counter


def deserialize(device_description):
    make_counter()
    counter = get_counter()
    device_schema = RemoteNodeSchema()
    device_obj = device_schema.load(device_description)
    device_obj.hash_string = hash_string_from_string(json.dumps(device_description))
    return device_obj


def hash_string_from_string(input_string):
    return hex(
        int.from_bytes(hashlib.sha256(input_string.encode()).digest()[:4], "little")
    )
