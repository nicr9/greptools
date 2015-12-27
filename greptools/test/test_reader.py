import unittest

from mock import Mock
from tempfile import NamedTemporaryFile as TF

from ..reader.reader import BraceReader, replace_parens

class TestReaderHelperMethods(unittest.TestCase):
    def test_replace_parens_succeed(self):
        """Example method name in Java (taken from elasticsearch).

        Result should replace contents of brackets with "..."."""
        code = "public boolean download(URL source, Path dest, @Nullable DownloadProgress progress, TimeValue timeout) throws Exception"
        expected = "public boolean download(...) throws Exception"

        results = replace_parens(code)
        self.assertEqual(expected, results)

    def test_replace_parens_no_op(self):
        """If there are no brackets, then don't change the text."""
        code = "public class HttpDownloadHelper"

        result = replace_parens(code)
        self.assertEqual(code, result)

    def test_replace_parens_nested(self):
        """Assert greedy matching is used in the event of nested brackets.

        Substitution should replace full contents of the outer bracket pair."""
        simple = "method_name(arg1, arg_wrapper(arg2), arg3)"
        expected = "method_name(...)"

        results = replace_parens(simple)
        self.assertEqual(expected, results)

        complicated = "how(are(you(today))) my(lad)"
        expected = "how(...) my(...)"

        results = replace_parens(complicated)
        self.assertEqual(expected, results)

    def test_replace_parens_empty(self):
        """Should work with empty parenthesis as well."""
        simple = "method_name()"
        expected = "method_name(...)"

        results = replace_parens(simple)
        self.assertEqual(expected, results)

        nested = "method_name(arg())"
        expected = "method_name(...)"

        results = replace_parens(nested)
        self.assertEqual(expected, results)

        consecutive = "method1() method2()"
        expected = "method1(...) method2(...)"

        results = replace_parens(consecutive)
        self.assertEqual(expected, results)

    def test_replace_parens_incomplete(self):
        """Incomplete bracket pair should be ignored."""
        code = "method_name(arg1, "

        results = replace_parens(code)
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
