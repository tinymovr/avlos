from avlos.generators.filters import as_include
import unittest


class TestFunctions(unittest.TestCase):
    def test_jinja_as_include_filter(self):
        self.assertEqual("<test.h>", as_include("test.h"))
        self.assertEqual("<test.h>", as_include("<test.h>"))
        self.assertEqual('"test.h"', as_include('"test.h"'))
