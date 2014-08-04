import unittest
from mock import Mock
from ..reader.reader import BraceReader

class TestBraceReader(unittest.TestCase):
    def setUp(self):
        """Sets up a BraceReader object for use in the tests."""
        config = Mock()
        config.debug = False
        self.br = BraceReader(config)

    def test_recursive_rfind_simple(self):
        """As simple a test as possilble."""
        example = "This is(a test)"
        expected = 7
        result = self.br.recursive_rfind(example, '(', ')', 10)
        self.assertEqual(result, expected)

    def test_recursive_rfind_fake_code(self):
        """A test against some psudo-code."""
        example = """class Test {
    func test() {
        this will be skipped;
        }
    Blah blah blah
    }
"""
        expected = 11
        result = self.br.recursive_rfind(example, '{', '}', 76)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
