import unittest
import json

class GrepTree(object):
    LINES = 'lines'

    def __init__(self, data={}):
        self.data = data
        self._count = 0

    @classmethod
    def load(cls, path):
        with open(path, 'r') as inp_file:
            return cls(json.load(inp_file))

    def dump(self, path):
        with open(path, 'w') as outp_file:
            flat = json.dumps(self.context, indent=4)
            outp_file.write(flat)

    def touch(self, file_path):
        # Add file path node to tree
        if not file_path in self.data:
            self.data[file_path] = {}

    def append(self, file_path, line_number, line_text, cntx_list):
        """
        Adds a line to the context tree.
        """
        # Step through context tree, creating nodes along the way
        pointer = self.data[file_path]
        for step in cntx_list:
            if step not in pointer:
                pointer[step] = {}
            pointer = pointer[step]
        if self.LINES not in pointer:
            pointer[self.LINES] = []

        # Add line_number + line_text to context
        pointer[self.LINES].append((line_number, line_text))

        # Increment counter
        self._count += 1

class TestGrepTree(unittest.TestCase):
    def test_load(self):
        # Test path that doesn't exist
        # Test path that doesn't contain vaild json
        # Test path that doesn't contain a json dict (but still valid json)
        # Test path that looks legit
        pass

    def test_append(self):
        pass

if __name__ == "__main__":
    unittest.main()
