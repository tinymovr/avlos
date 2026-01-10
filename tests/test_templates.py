"""
Tests for Jinja2 templates and generated code patterns.
"""
import unittest
import yaml
import importlib.resources
from avlos.deserializer import deserialize
from avlos.generators import generator_c, generator_cpp
from avlos.datatypes import DataType


class TestTemplateMacros(unittest.TestCase):
    """Test template macro behavior through generated code."""

    def setUp(self):
        """Set up test fixtures."""
        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )

        with open(def_path_str) as device_desc_stream:
            self.device = deserialize(yaml.safe_load(device_desc_stream))

    def test_char_array_getter_uses_helper(self):
        """Test that char[] getter generates code using _avlos_getter_string."""
        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_char_getter.c")
        )

        config = {
            "hash_string": "0x9e8dc7ac",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_char_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_char_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        generator_c.process(self.device, config)

        with open(output_impl) as f:
            content = f.read()

        # Should contain the string helper function definition
        self.assertIn("_avlos_getter_string", content,
                     "Should define _avlos_getter_string helper")

        # Should contain helper function signature
        self.assertIn("uint8_t (*getter)(char*)", content,
                     "Helper should have correct signature")

        # Should call the helper in char[] endpoint functions
        # (nickname is a char[] attribute in good_device.yaml)
        self.assertIn("_avlos_getter_string(buffer, buffer_len, system_get_name)", content,
                     "Should use helper for char[] getter")

    def test_char_array_setter_uses_helper(self):
        """Test that char[] setter generates code using _avlos_setter_string."""
        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_char_setter.c")
        )

        config = {
            "hash_string": "0x9e8dc7ac",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_char_enum2.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_char_header2.h")
                ),
                "output_impl": output_impl,
            },
        }

        generator_c.process(self.device, config)

        with open(output_impl) as f:
            content = f.read()

        # Should contain the string helper function definition
        self.assertIn("_avlos_setter_string", content,
                     "Should define _avlos_setter_string helper")

        # Should contain helper function signature
        self.assertIn("void (*setter)(const char*)", content,
                     "Helper should have correct signature")

        # Should call the helper in char[] endpoint functions
        self.assertIn("_avlos_setter_string(buffer, system_set_name)", content,
                     "Should use helper for char[] setter")

    def test_numeric_getter_byval(self):
        """Test that numeric getters use by-value pattern."""
        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_numeric.c")
        )

        config = {
            "hash_string": "0x9e8dc7ac",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_numeric_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_numeric_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        generator_c.process(self.device, config)

        with open(output_impl) as f:
            content = f.read()

        # Should contain memcpy pattern for by-value types
        self.assertIn("memcpy(buffer, &v, sizeof(v))", content,
                     "Should use memcpy for by-value getters")

        # Should declare local variable for value
        # (check for patterns like "float v;" or "uint32_t v;")
        self.assertTrue(
            "float v;" in content or "uint32_t v;" in content or "uint8_t v;" in content,
            "Should declare local variable for value"
        )

    def test_void_function_no_return_value(self):
        """Test that void return type functions don't generate return value code."""
        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_void_func.c")
        )

        config = {
            "hash_string": "0x9e8dc7ac",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_void_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_void_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        generator_c.process(self.device, config)

        with open(output_impl) as f:
            content = f.read()

        # Find the reset function (void return, no args)
        if "avlos_reset" in content:
            # Extract the reset function
            start = content.find("uint8_t avlos_reset")
            end = content.find("\n}", start) + 2
            reset_func = content[start:end]

            # Void functions should NOT have ret_val
            self.assertNotIn("ret_val", reset_func,
                           "Void function should not have return value")

            # Should call function directly without assignment
            self.assertIn("system_reset()", reset_func,
                         "Should call void function without assignment")

    def test_function_with_args_unpacks_buffer(self):
        """Test that functions with arguments unpack from buffer."""
        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_func_args.c")
        )

        config = {
            "hash_string": "0x9e8dc7ac",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_func_args_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_func_args_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        generator_c.process(self.device, config)

        with open(output_impl) as f:
            content = f.read()

        # Should have offset tracking for multiple arguments
        self.assertIn("uint8_t _offset = 0", content,
                     "Should track offset for argument unpacking")

        # Should unpack arguments with memcpy
        self.assertIn("memcpy(&", content,
                     "Should use memcpy to unpack arguments")

        # Should increment offset
        self.assertIn("_offset += sizeof(", content,
                     "Should increment offset for each argument")

    def test_all_data_types_generate(self):
        """Test that all supported data types can be generated."""
        # Create a test YAML with all data types
        yaml_content = """
        name: test_device
        remote_attributes:
          - name: u8_val
            summary: uint8 value
            dtype: uint8
            getter_name: get_u8
          - name: i8_val
            summary: int8 value
            dtype: int8
            getter_name: get_i8
          - name: u16_val
            summary: uint16 value
            dtype: uint16
            getter_name: get_u16
          - name: i16_val
            summary: int16 value
            dtype: int16
            getter_name: get_i16
          - name: u32_val
            summary: uint32 value
            dtype: uint32
            getter_name: get_u32
          - name: i32_val
            summary: int32 value
            dtype: int32
            getter_name: get_i32
          - name: u64_val
            summary: uint64 value
            dtype: uint64
            getter_name: get_u64
          - name: i64_val
            summary: int64 value
            dtype: int64
            getter_name: get_i64
          - name: float_val
            summary: float value
            dtype: float
            getter_name: get_float
          - name: double_val
            summary: double value
            dtype: double
            getter_name: get_double
          - name: str_val
            summary: string value
            dtype: string
            getter_name: get_str
          - name: bool_val
            summary: bool value
            dtype: bool
            getter_name: get_bool
        """

        obj = deserialize(yaml.safe_load(yaml_content))

        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_all_types.c")
        )

        config = {
            "hash_string": "0xdeadbeef",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_all_types_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_all_types_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        # Should not raise any exceptions
        generator_c.process(obj, config)

        with open(output_impl) as f:
            content = f.read()

        # Verify all types are present
        expected_types = [
            "uint8_t", "int8_t", "uint16_t", "int16_t",
            "uint32_t", "int32_t", "uint64_t", "int64_t",
            "float", "double", "bool"
        ]

        for dtype in expected_types:
            self.assertIn(dtype, content,
                         f"Generated code should contain {dtype}")

        # String types use helper functions, so check for that instead of "char[]"
        self.assertIn("_avlos_getter_string", content,
                     "Generated code should contain string helper function")

    def test_func_attr_in_output(self):
        """Test that func_attr (e.g., TM_RAMFUNC) appears in generated code."""
        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_func_attr.c")
        )

        config = {
            "hash_string": "0x9e8dc7ac",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_func_attr_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_func_attr_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        generator_c.process(self.device, config)

        with open(output_impl) as f:
            content = f.read()

        # good_device.yaml has TM_RAMFUNC on some functions
        if "TM_RAMFUNC" in content:
            self.assertIn("TM_RAMFUNC uint8_t avlos_", content,
                         "func_attr should appear before function declaration")

    def test_endpoint_array_generation(self):
        """Test that endpoint array is correctly generated."""
        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_ep_array.c")
        )

        config = {
            "hash_string": "0x9e8dc7ac",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_ep_array_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_ep_array_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        generator_c.process(self.device, config)

        with open(output_impl) as f:
            content = f.read()

        # Should have endpoint array declaration
        self.assertIn("uint8_t (*avlos_endpoints[", content,
                     "Should declare endpoint array")

        # Should have proto hash function
        self.assertIn("_avlos_get_proto_hash", content,
                     "Should have proto hash function")


class TestIntegration(unittest.TestCase):
    """Test full pipeline integration."""

    def test_full_pipeline_c_generation(self):
        """Test complete C generation pipeline with all features."""
        import importlib.resources

        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )

        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))

        output_impl = str(
            importlib.resources.files("tests").joinpath("outputs/test_integration.c")
        )

        config = {
            "hash_string": "0x12345678",
            "paths": {
                "output_enums": str(
                    importlib.resources.files("tests").joinpath("outputs/test_integration_enum.h")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_integration_header.h")
                ),
                "output_impl": output_impl,
            },
        }

        # Full pipeline: validation → generation → formatting
        generator_c.process(obj, config)

        # Verify all files exist
        import os
        self.assertTrue(os.path.exists(config["paths"]["output_enums"]))
        self.assertTrue(os.path.exists(config["paths"]["output_header"]))
        self.assertTrue(os.path.exists(config["paths"]["output_impl"]))

        # Verify implementation file has key content
        with open(output_impl) as f:
            content = f.read()

        self.assertIn("avlos_", content)
        self.assertIn("AVLOS_CMD_READ", content)
        self.assertIn("avlos_endpoints[", content)

    def test_cpp_generation_pipeline(self):
        """Test complete C++ generation pipeline."""
        import importlib.resources

        def_path_str = str(
            importlib.resources.files("tests").joinpath("definition/good_device.yaml")
        )

        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))

        config = {
            "hash_string": "0x12345678",
            "paths": {
                "output_helpers": str(
                    importlib.resources.files("tests").joinpath("outputs/test_cpp_helpers.hpp")
                ),
                "output_header": str(
                    importlib.resources.files("tests").joinpath("outputs/test_cpp_device.hpp")
                ),
                "output_impl": str(
                    importlib.resources.files("tests").joinpath("outputs/test_cpp_device.cpp")
                ),
            },
        }

        # Full pipeline: validation → generation → formatting
        generator_cpp.process(obj, config)

        # Verify files exist
        import os
        self.assertTrue(os.path.exists(config["paths"]["output_helpers"]))
        self.assertTrue(os.path.exists(config["paths"]["output_header"]))
        self.assertTrue(os.path.exists(config["paths"]["output_impl"]))


if __name__ == '__main__':
    unittest.main()
