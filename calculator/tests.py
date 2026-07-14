import unittest
from pkg.calculator import Calculator


class TestCalculator(unittest.TestCase):
    def test_simple_precedence(self):
        self.assertEqual(Calculator().evaluate("3 + 5 * 2"), 13)

    def test_parentheses_free_precedence(self):
        self.assertEqual(Calculator().evaluate("10 - 2 * 3"), 4)

    def test_addition(self):
        self.assertEqual(Calculator().evaluate("2 + 2"), 4)

    def test_division(self):
        self.assertEqual(Calculator().evaluate("10 / 2 + 3"), 8)


if __name__ == "__main__":
    unittest.main()
