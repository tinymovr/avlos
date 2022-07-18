import yaml
import importlib.resources
from avlos.deserializer import deserialize
from avlos.unit_field import get_registry
import unittest
from tests.dummy_channel import DummyChannel

_reg = get_registry()


class TestRemoteObjects(unittest.TestCase):
    def test_read_properties(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()

            self.assertEqual(0, obj.Vbus)
            obj._channel.set_value(12.0)
            self.assertEqual(12.0 * _reg("volt"), obj.Vbus)
            obj._channel.set_value(24.0)
            self.assertEqual(24.0 * _reg("volt"), obj.Vbus)

            obj._channel.set_value(0.1)
            self.assertEqual(0.1 * _reg("ohm"), obj.motor.R)

            obj.controller.set_pos_vel_setpoints(0, 0)

    def test_non_existent_attributes(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()
            with self.assertRaises(AttributeError):
                val = obj.foo
                print(val)
            with self.assertRaises(AttributeError):
                val = obj.controller.bar
                print(val)


        
