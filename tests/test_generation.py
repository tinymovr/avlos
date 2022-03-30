
import yaml
import importlib.resources
from avlos.deserializer import deserialize
import avlos.generators.generator_c as generator_c
import marshmallow
import pint
import unittest
from pprint import pprint


class TestGeneration(unittest.TestCase):

    def test_c_output_manual(self):
        def_path_str = str(importlib.resources.files('tests').joinpath('definition/good_device.yaml'))
        out_path_str = str(importlib.resources.files('tests').joinpath('outputs/impl.c'))
        with open(def_path_str) as system_description:
            obj = deserialize(yaml.safe_load(system_description))
            config = {
                "output_file": out_path_str,
                "c_includes": {
                    "src/common.h"
                }
            }
            generator_c.process(obj, config)