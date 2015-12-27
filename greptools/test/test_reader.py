import unittest

from mock import Mock
from tempfile import NamedTemporaryFile as TF

from ..reader.reader import BraceReader, hide_method_args

class TestReaderHelperMethods(unittest.TestCase):
    def test_hide_method_args_succeed(self):
        """Example method name in Java (taken from elasticsearch).

        Result should replace contents of brackets with "..."."""
        code = "public boolean download(URL source, Path dest, @Nullable DownloadProgress progress, TimeValue timeout) throws Exception"
        expected = "public boolean download(...) throws Exception"

        results = hide_method_args(code)
        self.assertEqual(expected, results)

    def test_hide_method_args_no_op(self):
        """If there are no brackets, then don't change the text."""
        code = "public class HttpDownloadHelper"

        result = hide_method_args(code)
        self.assertEqual(code, result)

    def test_hide_method_args_nested(self):
        """Assert greedy matching is used in the event of nested brackets.

        Substitution should replace full contents of the outer bracket pair."""
        code = "method_name(arg1, arg_wrapper(arg2), arg3)"
        expected = "method_name(...)"

        results = hide_method_args(code)
        self.assertEqual(expected, results)

    def test_hide_method_args_incomplete(self):
        """Incomplete bracket pair should be ignored."""
        code = "method_name(arg1, "

        results = hide_method_args(code)
        self.assertEqual(code, results)

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

    def test_get_context(self):
        text = """class A(blah) {
    func b(blah, blah) {
        sample text;
    }
}
"""
        with TF(delete=False) as outp:
            outp.write(text)
            file_name = outp.name

        print self.br.get_context(file_name, 3)


if __name__ == "__main__":
    unittest.main()
