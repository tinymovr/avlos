import json
import hashlib
from avlos.definition import RemoteNodeSchema
from avlos.counter import make_counter


def deserialize(device_description):
    make_counter()
    device_schema = RemoteNodeSchema()
    device_obj = device_schema.load(device_description)
    dev_desc = json.dumps(device_description)
    device_obj.hash_string = hash_string_from_string(dev_desc)
    device_obj.hash_int32 = hash_int_from_string(dev_desc)
    return device_obj


def hash_string_from_string(input_string):
    return hex(hash_int_from_string(input_string))


def hash_int_from_string(input_string):
    return int.from_bytes(hashlib.sha256(input_string.encode()).digest()[:4], "little")
