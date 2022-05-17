import yaml
import importlib.resources
from avlos.deserializer import deserialize
import marshmallow
import pint
import unittest
from tests.dummy_channel import DummyChannel


class TestRemoteObjects(unittest.TestCase):
    def test_properties(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()

            self.assertEqual(0, obj.Vbus)
            obj.controller.set_pos_vel_setpoints(0, 0)
