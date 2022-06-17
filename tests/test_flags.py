from avlos.flags_field import Flags
import unittest


class TestFlags(unittest.TestCase):

    def setUp(self):
        self.test_flag = Flags(["ONE", "TWO", "FOUR"])
        self.reference = [
            ["NONE"],
            ["ONE"],
            ["TWO"],
            ["ONE", "TWO"],
            ["FOUR"],
            ["ONE", "FOUR"],
            ["TWO", "FOUR"],
            ["ONE", "TWO", "FOUR"]
        ]

    def test_number_to_flags_list(self):
        for i in range(8):
            self.assertEqual(self.test_flag.match(i), self.reference[i])

    def test_flags_list_to_number(self):
        for i in range(8):
            self.assertEqual(self.test_flag.mask(self.reference[i]), i)