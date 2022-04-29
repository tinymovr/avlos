import json
import hashlib
from avlos.definition import RemoteNodeSchema


class Counter:
    def __init__(self):
        self.count = 0

    def next(self):
        cnt = self.count
        self.count += 1
        return cnt


def make_counter(reset=False):
    pass


def deserialize(device_description):
    device_schema = RemoteNodeSchema(Counter())
    device_obj = device_schema.load(device_description)
    device_obj.hash_string = hash_string_from_string(json.dumps(device_description))
    return device_obj


def hash_string_from_string(input_string):
    return hex(
        int.from_bytes(hashlib.sha256(input_string.encode()).digest()[:4], "little")
    )
