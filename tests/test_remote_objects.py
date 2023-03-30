import yaml
import importlib.resources
from avlos.deserializer import deserialize
from avlos.unit_field import get_registry
import unittest
from tests.dummy_channel import DummyChannel

_reg = get_registry()


class TestRemoteObjects(unittest.TestCase):
    def test_read_remote_properties(self):
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

            obj.channel.set_value("lalala")
            self.assertEqual(obj.nickname, "lalala")

            obj.controller.set_pos_vel_setpoints(0, 0)

            obj._channel.write_on()
            obj.nickname = "other"
            obj._channel.write_off()
            self.assertEqual(obj.nickname, "other")

    def test_remote_enum(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:

            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()
            modes = obj.controller.remote_attributes["mode"].options
            obj._channel.set_value(0)
            self.assertEqual(obj.controller.mode, modes.IDLE)
            obj._channel.set_value(1)
            self.assertEqual(obj.controller.mode, modes.CLOSED_LOOP)

    def test_remote_function_call(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()

        self.assertEqual(0, obj.controller.set_pos_vel_setpoints(1, 2))
        obj._channel.set_value(100.0)
        self.assertEqual(100 * _reg("tick"), obj.controller.set_pos_vel_setpoints(0, 0))

    def test_non_existent_remote_attributes_fail(self):
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

    def test_meta_dictionary(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            self.assertEqual(1, len(obj.errors.meta))
            self.assertEqual("ok", obj.errors.meta["lalala"])
            self.assertEqual(1, len(obj.reset.meta))
            self.assertEqual(True, obj.reset.meta["reload_data"])
            self.assertEqual(0, len(obj.sn.meta))
            with self.assertRaises(KeyError):
                d = obj.sn.meta["reload_data"]
