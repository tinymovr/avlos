import yaml
import importlib.resources
import urllib.request
from avlos.deserializer import deserialize
import marshmallow
import pint
import unittest
from tests.dummy_channel import DummyChannel


class TestDeserialization(unittest.TestCase):
    def test_success(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            obj = deserialize(yaml.safe_load(device_description))
            obj._channel = DummyChannel()
            print(obj)

    def test_success_url(self):
        device_desc_string = urllib.request.urlopen(
            "https://raw.githubusercontent.com/tinymovr/avlos/main/tests/definition/good_device.yaml"
        ).read()
        obj = deserialize(yaml.safe_load(device_desc_string))
        obj._channel = DummyChannel()
        print(obj)

    def test_undefined_unit(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath(
                "definition/bad_device_unit.yaml"
            )
        )
        with open(def_path_str) as device_description:
            with self.assertRaises(pint.errors.UndefinedUnitError):
                deserialize(yaml.safe_load(device_description))

    def test_bitmask_labels(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        with open(def_path_str) as device_description:
            device = deserialize(yaml.safe_load(device_description))
            device._channel = DummyChannel()
            self.assertEqual(device.errors.value, 0)

    def test_empty_bitmask_labels(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath(
                "definition/bad_device_bitmask.yaml"
            )
        )
        with open(def_path_str) as device_description:
            with self.assertRaises(marshmallow.exceptions.ValidationError):
                deserialize(yaml.safe_load(device_description))

    def test_version_field_present(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath(
                "definition/obsolete_device.yaml"
            )
        )
        with open(def_path_str) as device_description:
            device = deserialize(yaml.safe_load(device_description))
            device._channel = DummyChannel()
            self.assertEqual(device.errors.value, 0)

    def test_validation_fail(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath(
                "definition/bad_device_name.yaml"
            )
        )
        with open(def_path_str) as device_description:
            with self.assertRaises(marshmallow.exceptions.ValidationError):
                deserialize(yaml.safe_load(device_description))
