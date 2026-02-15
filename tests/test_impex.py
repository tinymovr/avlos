import importlib.resources
import json
import unittest

import yaml

from avlos.deserializer import deserialize
from avlos.json_codec import AvlosEncoder
from avlos.unit_field import get_registry
from tests.dummy_channel import DummyChannel

_reg = get_registry()


class TestImpex(unittest.TestCase):
    """Tests for export_values / import_values round-trip."""

    def _load_device(self):
        def_path_str = str(importlib.resources.files("tests").joinpath("definition/good_device.yaml"))
        with open(def_path_str) as f:
            obj = deserialize(yaml.safe_load(f))
        obj._channel = DummyChannel()
        return obj

    def test_import_export_root_object(self):
        obj = self._load_device()
        obj._channel.set_value(0)
        func = obj.motor.remote_attributes["R"]
        root = func.root
        self.assertEqual(obj, root)
        values = root.export_values()
        json_string = json.dumps(values, cls=AvlosEncoder)
        imported_values = json.loads(json_string)
        root.import_values(imported_values)

    def test_import_restores_values_after_json_roundtrip(self):
        """
        Export with a known value, change the default, import, and
        verify each export-tagged attribute returns the original value.

        This exercises both code paths in import_values:
        - string data (attributes with units, serialised by AvlosEncoder)
        - non-string data (unit-less attributes, plain floats from JSON)
        """
        obj = self._load_device()

        # 1. Seed a known non-zero value so exports are meaningful
        obj._channel.set_value(3.14)
        root = obj

        # 2. Export → JSON round-trip (mimics file save / load)
        exported = root.export_values()
        self.assertIsNotNone(exported)
        json_str = json.dumps(exported, cls=AvlosEncoder)
        reimported = json.loads(json_str)

        # Sanity: motor.R should be a string with units
        self.assertIsInstance(reimported["motor"]["R"], str)
        self.assertIn("ohm", reimported["motor"]["R"])

        # Sanity: motor.gain should be a plain float (unit-less)
        self.assertIsInstance(reimported["motor"]["gain"], float)

        # 3. Change the default so get_value would return something else
        #    if import silently fails
        obj._channel.set_value(0)
        obj._channel.write_on()

        # 4. Import
        root.import_values(reimported)

        # 5. Verify: each export-tagged attribute should return ~3.14
        R_val = obj.motor.R
        self.assertAlmostEqual(R_val.magnitude, 3.14, places=2, msg="motor.R not restored after import")

        L_val = obj.motor.L
        self.assertAlmostEqual(L_val.magnitude, 3.14, places=2, msg="motor.L not restored after import")

        bw_val = obj.encoder.bandwidth
        self.assertAlmostEqual(bw_val.magnitude, 3.14, places=2, msg="encoder.bandwidth not restored after import")

        gain_val = obj.motor.gain
        self.assertAlmostEqual(gain_val, 3.14, places=2, msg="motor.gain (unit-less) not restored after import")
