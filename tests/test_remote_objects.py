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

    def test_remote_enum_read(self):
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

    def test_remote_enum_write(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()
            modes = obj.controller.remote_attributes["mode"].options
            obj._channel.write_on()

            # Test setting the value using an integer
            obj.controller.mode = 0
            self.assertEqual(obj._channel.value, 0)

            # Test setting the value using another integer
            obj.controller.mode = 1
            self.assertEqual(obj._channel.value, 1)

            # Test setting the value using an enum member
            obj.controller.mode = modes.IDLE
            self.assertEqual(obj._channel.value, 0)

            # Test setting the value using another enum member
            obj.controller.mode = modes.CLOSED_LOOP
            self.assertEqual(obj._channel.value, 1)

            # Test setting the value using a string corresponding to an enum member
            obj.controller.mode = "IDLE"
            self.assertEqual(obj._channel.value, 0)

            # Test setting the value using another string corresponding to an enum member
            obj.controller.mode = "CLOSED_LOOP"
            self.assertEqual(obj._channel.value, 1)

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

    def test_remote_function_call_w_units(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()

        obj._channel.write_on()
        obj.move_to(1 * _reg("turn"))
        self.assertEqual(8192, obj._channel.value)
        obj.move_to(-100)
        self.assertEqual(-100, obj._channel.value)
        obj._channel.write_off()

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
