import yaml
import importlib.resources
from avlos.deserializer import deserialize
from avlos.unit_field import get_registry
import unittest
from tests.dummy_channel import DummyChannel

_reg = get_registry()


class TestImpex(unittest.TestCase):
    
    def test_import_export(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:

            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()

            obj._channel.set_value(0)

            values = obj.export_values()

            obj.import_values(values)

    def test_import_export_root_object(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()

            obj._channel.set_value(0)

            func = obj.move_to

            root = func.root

            self.assertEqual(obj, root)

            values = root.export_values()

            root.import_values(values)

            
 
