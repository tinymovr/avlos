import json
import yaml
import importlib.resources
from avlos.deserializer import deserialize
from avlos.unit_field import get_registry
from avlos.json_codec import AvlosEncoder
import unittest
from tests.dummy_channel import DummyChannel


class TestImpex(unittest.TestCase):
    def test_import_export_root_object(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()
            obj._channel.set_value(0)
            func = obj.motor.remote_attributes["R"]
            root = func.root
            self.assertEqual(obj, root)
            values = root.export_values()
            json_string = json.dumps(values, cls=AvlosEncoder)
            imported_values = json.loads(json_string)
            root.import_values(imported_values)
