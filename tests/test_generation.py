import yaml
import importlib.resources
from avlos.deserializer import deserialize
from avlos.processor import process, process_file
import avlos.generators.generator_c as generator_c
import avlos.generators.generator_rst as generator_rst
import marshmallow
import pint
import unittest
from pprint import pprint


class TestGeneration(unittest.TestCase):
    def test_c_output_manual(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        header_path_str = str(
            importlib.resources.files("tests").joinpath("outputs/test.h")
        )
        impl_path_str = str(
            importlib.resources.files("tests").joinpath("outputs/test.c")
        )
        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))
            config = {
                "hash_string": "0x9e8dc7ac",
                "paths": {
                    "output_header": header_path_str,
                    "output_impl": impl_path_str,
                },
                "c_includes": {"src/common.h"},
            }
            generator_c.process(obj, config)

    def test_rst_output_manual(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        out_path_str = str(
            importlib.resources.files("tests").joinpath("outputs/test.rst")
        )
        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))
            config = {
                "hash_string": "0x9e8dc7ac",
                "paths": {"output_file": out_path_str},
            }
            generator_rst.process(obj, config)

    def test_output_config(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        config_file_path_str = str(
            importlib.resources.files("tests").joinpath("definition/output_config.yaml")
        )
        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))
            process_file(obj, config_file_path_str)
