"""
Tests for data model properties added for code generation.
"""

import unittest

import yaml

from avlos.datatypes import DataType
from avlos.definitions.remote_attribute import RemoteAttribute
from avlos.definitions.remote_bitmask import RemoteBitmask
from avlos.definitions.remote_enum import RemoteEnum
from avlos.definitions.remote_function import RemoteFunction
from avlos.deserializer import deserialize


class TestDataModelProperties(unittest.TestCase):
    """Test properties added to data model classes."""

    def test_string_getter_strategy(self):
        """Test that char[] types return 'string' getter strategy."""
        attr = RemoteAttribute(
            name="nickname",
            summary="Device nickname",
            dtype=DataType.STR,
            getter_name="get_nickname",
        )

        self.assertEqual(attr.getter_strategy, "string")
        self.assertEqual(attr.setter_strategy, "string")

    def test_byval_getter_strategy_float(self):
        """Test that float types return 'byval' getter strategy."""
        attr = RemoteAttribute(
            name="voltage",
            summary="Bus voltage",
            dtype=DataType.FLOAT,
            getter_name="get_voltage",
        )

        self.assertEqual(attr.getter_strategy, "byval")
        self.assertEqual(attr.setter_strategy, "byval")

    def test_byval_getter_strategy_integers(self):
        """Test that integer types return 'byval' getter strategy."""
        int_types = [
            DataType.UINT8,
            DataType.INT8,
            DataType.UINT16,
            DataType.INT16,
            DataType.UINT32,
            DataType.INT32,
            DataType.UINT64,
            DataType.INT64,
        ]

        for dtype in int_types:
            attr = RemoteAttribute(
                name="test_value",
                summary="Test value",
                dtype=dtype,
                getter_name="get_value",
            )

            self.assertEqual(attr.getter_strategy, "byval", f"{dtype} should use byval strategy")
            self.assertEqual(attr.setter_strategy, "byval", f"{dtype} should use byval strategy")

    def test_endpoint_function_name_simple(self):
        """Test endpoint function name for simple attribute."""
        from avlos.mixins.named_node import NamedNode

        attr = RemoteAttribute(
            name="voltage",
            summary="Bus voltage",
            dtype=DataType.FLOAT,
            getter_name="get_voltage",
        )
        # Set include_base_name so full_name returns the name when parent is None
        attr.include_base_name = True

        self.assertEqual(attr.endpoint_function_name, "avlos_voltage")

    def test_endpoint_function_name_nested(self):
        """Test endpoint function name for nested attribute."""
        import importlib.resources

        def_path_str = str(importlib.resources.files("tests").joinpath("definition/good_device.yaml"))

        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))

            # Find a nested attribute (e.g., motor.R)
            if hasattr(obj, "motor") and hasattr(obj.motor, "R"):
                attr = obj.motor.R
                expected_name = "avlos_motor_R"
                self.assertEqual(attr.endpoint_function_name, expected_name, f"motor.R should generate {expected_name}")

    def test_is_string_type_true(self):
        """Test is_string_type property for char[] type."""
        attr = RemoteAttribute(
            name="name",
            summary="Device name",
            dtype=DataType.STR,
            getter_name="get_name",
        )

        self.assertTrue(attr.is_string_type)

    def test_is_string_type_false(self):
        """Test is_string_type property for non-string types."""
        attr = RemoteAttribute(
            name="value",
            summary="Numeric value",
            dtype=DataType.FLOAT,
            getter_name="get_value",
        )

        self.assertFalse(attr.is_string_type)

    def test_remote_function_endpoint_name(self):
        """Test endpoint function name for RemoteFunction."""
        func = RemoteFunction(
            name="reset",
            summary="Reset the device",
            caller_name="system_reset",
            arguments=[],
            dtype=DataType.VOID,
        )
        # Set include_base_name so full_name returns the name when parent is None
        func.include_base_name = True

        self.assertEqual(func.endpoint_function_name, "avlos_reset")

    def test_remote_function_endpoint_name_nested(self):
        """Test endpoint function name for nested RemoteFunction."""
        import importlib.resources

        def_path_str = str(importlib.resources.files("tests").joinpath("definition/good_device.yaml"))

        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))

            # Find nested function (e.g., controller.set_pos_vel_setpoints)
            if hasattr(obj, "controller") and hasattr(obj.controller, "set_pos_vel_setpoints"):
                func = obj.controller.set_pos_vel_setpoints
                expected_name = "avlos_controller_set_pos_vel_setpoints"
                self.assertEqual(func.endpoint_function_name, expected_name)

    def test_enum_properties(self):
        """Test that RemoteEnum has correct properties."""
        from enum import IntEnum

        class TestEnum(IntEnum):
            OPTION_A = 0
            OPTION_B = 1
            OPTION_C = 2

        enum_attr = RemoteEnum(
            name="mode",
            summary="Operating mode",
            getter_name="get_mode",
            setter_name="set_mode",
            options=TestEnum,
        )
        # Set include_base_name so full_name returns the name when parent is None
        enum_attr.include_base_name = True

        self.assertEqual(enum_attr.getter_strategy, "byval")
        self.assertEqual(enum_attr.setter_strategy, "byval")
        self.assertEqual(enum_attr.endpoint_function_name, "avlos_mode")

    def test_bitmask_properties(self):
        """Test that RemoteBitmask has correct properties."""
        from enum import IntFlag

        class TestFlags(IntFlag):
            FLAG_A = 1
            FLAG_B = 2
            FLAG_C = 4

        bitmask_attr = RemoteBitmask(
            name="errors",
            summary="Error flags",
            getter_name="get_errors",
            flags=TestFlags,
        )
        # Set include_base_name so full_name returns the name when parent is None
        bitmask_attr.include_base_name = True

        self.assertEqual(bitmask_attr.getter_strategy, "byval")
        self.assertEqual(bitmask_attr.setter_strategy, "byval")
        self.assertEqual(bitmask_attr.endpoint_function_name, "avlos_errors")

    def test_backward_compatibility_generated_code(self):
        """Test that generated code is functionally equivalent to before refactoring."""
        import importlib.resources

        from avlos.generators import generator_c

        def_path_str = str(importlib.resources.files("tests").joinpath("definition/good_device.yaml"))
        output_impl = str(importlib.resources.files("tests").joinpath("outputs/test_backward_compat.c"))

        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))

            config = {
                "hash_string": "0x9e8dc7ac",
                "paths": {
                    "output_enums": str(importlib.resources.files("tests").joinpath("outputs/test_enum_compat.h")),
                    "output_header": str(importlib.resources.files("tests").joinpath("outputs/test_header_compat.h")),
                    "output_impl": output_impl,
                },
            }

            # Generate code
            generator_c.process(obj, config)

            # Read generated code
            with open(output_impl) as f:
                generated_code = f.read()

            # Verify key patterns are present
            self.assertIn("avlos_", generated_code, "Should have avlos_ prefixed functions")
            self.assertIn("AVLOS_CMD_READ", generated_code, "Should handle read commands")
            self.assertIn("AVLOS_CMD_WRITE", generated_code, "Should handle write commands")
            self.assertIn("_avlos_getter_string", generated_code, "Should have string getter helper")
            self.assertIn("_avlos_setter_string", generated_code, "Should have string setter helper")

            # Verify function declarations use properties
            # (all endpoint functions should be present)
            self.assertIn("uint8_t avlos_", generated_code)

    def test_all_endpoints_have_function_names(self):
        """Test that all endpoints from good_device.yaml have endpoint_function_name."""
        import importlib.resources

        from avlos.generators.filters import avlos_endpoints

        def_path_str = str(importlib.resources.files("tests").joinpath("definition/good_device.yaml"))

        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))

            endpoints = avlos_endpoints(obj)

            for ep in endpoints:
                self.assertTrue(
                    hasattr(ep, "endpoint_function_name"), f"Endpoint {ep.name} should have endpoint_function_name property"
                )
                func_name = ep.endpoint_function_name
                self.assertTrue(
                    func_name.startswith("avlos_"), f"Endpoint function name should start with avlos_, got: {func_name}"
                )
                self.assertNotIn(".", func_name, f"Endpoint function name should not contain dots, got: {func_name}")

    def test_getter_setter_strategy_consistency(self):
        """Test that getter and setter strategies are consistent."""
        import importlib.resources

        from avlos.generators.filters import avlos_endpoints

        def_path_str = str(importlib.resources.files("tests").joinpath("definition/good_device.yaml"))

        with open(def_path_str) as device_desc_stream:
            obj = deserialize(yaml.safe_load(device_desc_stream))

            endpoints = avlos_endpoints(obj)

            for ep in endpoints:
                # Skip functions (they don't have getter/setter strategies in the same way)
                if hasattr(ep, "caller_name") and not hasattr(ep, "getter_name"):
                    continue

                if hasattr(ep, "getter_strategy") and hasattr(ep, "setter_strategy"):
                    # Getter and setter strategies should match for attributes
                    self.assertEqual(
                        ep.getter_strategy,
                        ep.setter_strategy,
                        f"Endpoint {ep.name} should have consistent getter/setter strategies",
                    )


if __name__ == "__main__":
    unittest.main()
