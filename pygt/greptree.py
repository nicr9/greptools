import unittest
import json

def count_lines(subtree):
    """Convienience function to count the number of lines in a subtree."""
    count = 0
    for key, val in subtree.iteritems():
        if key == 'lines':
            count += len(val)
        else:
            count += count_lines(val)

    return count

class GrepTree(object):
    """Main data structure: used to store results nested into contexts."""
    LINES = 'lines'

    def __init__(self, data={}):
        self.data = data
        self._count = 0

    @classmethod
    def load(cls, inp_file):
        return cls(json.load(inp_file))

    @classmethod
    def load_path(cls, path):
        with open(path, 'r') as inp_file:
            return cls(json.load(inp_file))

    def dump_to_path(self, path):
        with open(path, 'w') as outp_file:
            flat = json.dumps(self.data, indent=4)
            outp_file.write(flat)

    def dump(self, outp_file):
        flat = json.dumps(self.data, indent=4)
        outp_file.write(flat)

    def touch(self, key, subtree=None):
        """Add empty node to subtree."""
        if subtree is None:
            subtree = self.data
        return subtree.setdefault(key, {})

    def append(self, file_path, line_number, line_text, cntx_list):
        """
        Adds a line to the context tree.
        """
        # Step through context tree, creating nodes along the way
        pointer = self.data[file_path]
        for step in cntx_list:
            pointer = self.touch(step, pointer)
        pointer.setdefault(self.LINES, [])

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
