from avlos.bitmask_field import Bitmask
import unittest


class TestBitmask(unittest.TestCase):

    def setUp(self):
        self.test_bitmask = Bitmask(["ONE", "TWO", "FOUR"])
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
            self.assertEqual(self.test_bitmask.match(i), self.reference[i])

    def test_flags_list_to_number(self):
        for i in range(8):
            self.assertEqual(self.test_bitmask.mask(self.reference[i]), i)