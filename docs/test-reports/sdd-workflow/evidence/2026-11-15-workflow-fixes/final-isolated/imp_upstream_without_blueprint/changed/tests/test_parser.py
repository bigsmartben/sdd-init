import unittest

from src.parser import parse


class ParseTests(unittest.TestCase):
    def test_empty_string_returns_empty_list(self):
        self.assertEqual(parse(''), [])

    def test_nonempty_strings_keep_comma_splitting(self):
        cases = (
            ('red,blue', ['red', 'blue']),
            ('red', ['red']),
            (',red,,blue,', ['', 'red', '', 'blue', '']),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(parse(value), expected)


if __name__ == '__main__':
    unittest.main()
