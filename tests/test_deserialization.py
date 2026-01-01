import yaml
import importlib.resources
import urllib.request
from avlos.deserializer import deserialize
from avlos.definitions.remote_node import RemoteNodeSchema
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

    def test_schema_field_initialization(self):
        """
        Test that RemoteNodeSchema can be instantiated without TypeError.
        This catches issues with using 'default' instead of 'dump_default' or 'load_default'
        in marshmallow 3.x field definitions, which causes:
        TypeError: Field.__init__() got an unexpected keyword argument 'default'
        """
        # This should not raise TypeError during schema instantiation
        schema = RemoteNodeSchema()

        # Test that schema can dump data with default values
        data = {"name": "test_node", "remote_attributes": []}
        result = schema.dump(data)

        # Verify the schema is working correctly
        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "test_node")

        # Test that optional fields with dump_default are included
        self.assertIn("func_attr", result)
        self.assertIsNone(result["func_attr"])
        self.assertIn("export", result)
        self.assertEqual(result["export"], False)
        self.assertIn("ep_id", result)
        self.assertEqual(result["ep_id"], -1)
