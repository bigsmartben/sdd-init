import unittest

from src.parser import parse


class ParserTests(unittest.TestCase):
    def test_empty_string_returns_empty_list(self):
        self.assertEqual(parse(""), [])

    def test_nonempty_string_splits_on_commas(self):
        self.assertEqual(parse("red,blue"), ["red", "blue"])
