import unittest
from mock import Mock
from os import remove as remove_file
from ..reader.markdownreader import MarkdownReader

class TestMdgt(unittest.TestCase):
    test_file = './test.md'
    file_text = """# Header 1

The keyword is 'journey'.

## Header 2

I'm going for a journey on a bus.

### Closed header ###

I hope I don't get sick on the bus.
"""

    @classmethod
    def setUpClass(cls):
        with open(cls.test_file, 'w') as outp:
            outp.write(cls.file_text)

    @classmethod
    def tearDownClass(cls):
        remove_file(cls.test_file)

    def setUp(self):
        config = Mock()
        config.debug = False
        config.case_off = False
        config.strict_on = False
        self.mdgt = MarkdownReader(config)

    def test_atx_headers(self):
        # search for 'journey'
        tree = self.mdgt.build_tree('journey')

        a = tree.data
        self.assertEqual([self.test_file], a.keys())

        b = a[self.test_file]
        self.assertEqual(['# Header 1'], b.keys())

        c = b['# Header 1']
        self.assertEqual(['## Header 2', 'lines'], c.keys())
        self.assertEqual([(3, "The keyword is 'journey'.")], c['lines'])

        d = c['## Header 2']
        self.assertEqual(['lines'], d.keys())
        self.assertEqual([(7, "I'm going for a journey on a bus.")], d['lines'])
