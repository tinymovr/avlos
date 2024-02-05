import yaml
import subprocess
from pathlib import Path
import importlib.resources
from avlos.deserializer import deserialize
from avlos.processor import process_with_config_file
import avlos.generators.generator_c as generator_c
import avlos.generators.generator_cpp as generator_cpp
import avlos.generators.generator_rst as generator_rst
from rstcheck_core import _extras, config as config_mod, runner
import unittest


class TestGeneration(unittest.TestCase):
    def test_c_output_manual(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        enum_path_str = str(
            importlib.resources.files("tests").joinpath("outputs/tm_enums.h")
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
                    "output_enums": enum_path_str,
                    "output_header": header_path_str,
                    "output_impl": impl_path_str,
                },
                "c_includes": {"src/common.h", "src/tm_enums.h"},
            }
            generator_c.process(obj, config)

            result = subprocess.run(
                ["cppcheck", "--error-exitcode=1", header_path_str, impl_path_str],
                stdout=subprocess.DEVNULL,
            )
            self.assertEqual(result.returncode, 0)

    def test_cpp_output_manual(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        helper_path_str = str(
            importlib.resources.files("tests").joinpath("outputs/tm_helpers.hpp")
        )
        header_path_str = str(
            importlib.resources.files("tests").joinpath("outputs/base_device.hpp")
        )
        impl_path_str = str(
            importlib.resources.files("tests").joinpath("outputs/base_device.cpp")
        )
        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))
            config = {
                "hash_string": "0x9e8dc7ac",
                "paths": {
                    "output_helpers": helper_path_str,
                    "output_header": header_path_str,
                    "output_impl": impl_path_str,
                },
                "header_includes": {"string"},
            }
            generator_cpp.process(obj, config)

            result = subprocess.run(
                ["cppcheck", "--error-exitcode=1", header_path_str, impl_path_str],
                stdout=subprocess.DEVNULL,
            )
            self.assertEqual(result.returncode, 0)

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

        rstcheck_config = config_mod.RstcheckConfig()
        path = Path(out_path_str)
        _runner = runner.RstcheckMainRunner(
            check_paths=[path], rstcheck_config=rstcheck_config, overwrite_config=False
        )
        _runner.check()
        _runner.print_result()

    def test_avlos_config(self):
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )
        config_file_path_str = str(
            importlib.resources.files("tests").joinpath("definition/avlos_config.yaml")
        )
        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))
            process_with_config_file(obj, config_file_path_str)
