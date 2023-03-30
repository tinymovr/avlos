from avlos.counter import get_counter, make_counter, delete_counter

import unittest


class TestCounter(unittest.TestCase):
    def test_make_counter_return(self):
        self.assertIsNone(make_counter())

    def test_get_counter(self):
        delete_counter()
        self.assertIsNone(get_counter())
        make_counter()
        self.assertIsNotNone(get_counter())

    def test_make_counter(self):
        make_counter()
        counter1 = get_counter()
        counter2 = get_counter()
        make_counter()
        counter3 = make_counter()
        self.assertEqual(counter1, counter2)
        self.assertNotEqual(counter1, counter3)

    def test_counter_next(self):
        make_counter()
        counter = get_counter()
        self.assertEqual(0, counter.count)
        self.assertEqual(0, counter.next())
        self.assertEqual(1, counter.next())
        self.assertEqual(counter.next() + 1, counter.count)
