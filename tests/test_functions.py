import unittest

from avlos.generators.filters import as_include, capitalize_first, file_from_path


class TestFunctions(unittest.TestCase):
    def test_file_from_path_filter(self):
        self.assertEqual("test_functions.py", file_from_path(__file__))

    def test_jinja_as_include_filter(self):
        self.assertEqual("<test.h>", as_include("test.h"))
        self.assertEqual("<test.h>", as_include("<test.h>"))
        self.assertEqual('"test.h"', as_include('"test.h"'))

    def test_capitalize_first(self):
        self.assertEqual(capitalize_first("bob Meadow"), "Bob Meadow")
