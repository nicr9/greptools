"""The GrepTree data structure centers around the idea of a `context`. A context
is essentially the function/class/method/file that a line belongs to. A GrepTree
is a nested tree-style collection of these contexts, with the furthest point on
each branch containing a list of lines that come from that context.
"""
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
    """Data structure for storing results as a tree of nested contexts."""
    LINES = 'lines'

    def __init__(self, data={}):
        self.data = data
        self._count = 0

    @classmethod
    def load(cls, inp_file):
        """Create GrepTree object from json file handler."""
        return cls(json.load(inp_file))

    @classmethod
    def load_path(cls, path):
        """Open json file as GrepTree object."""
        with open(path, 'r') as inp_file:
            return cls(json.load(inp_file))

    def dump_to_path(self, path):
        """JSON encode GrepTree object and write to file at path."""
        with open(path, 'w') as outp_file:
            self.dump(outp_file)

    def dump(self, outp_file):
        """JSON encode GrepTree object and write to file object."""
        flat = json.dumps(self.data, indent=4)
        outp_file.write(flat)

    def touch(self, key, subtree=None):
        """Add empty node to a subtree."""
        if subtree is None:
            subtree = self.data
        return subtree.setdefault(key, {})

    def touch_path(self, path, subtree=None):
        """Recursively adds a string of empty nodes to a subtree. 
        Returns the new subtree when it's done."""
        for step in path:
            subtree = self.touch(step, subtree)

        return subtree

    def append(self, file_path, line_number, line_text, cntx_list):
        """
        Adds a line to the tree creating any intermediate nodes along the way.
        """
        # Step through context tree, creating nodes along the way
        node_path = [file_path] + list(cntx_list)
        head = self.touch_path(node_path)

        # Add line_number + line_text to head of path
        lines = head.setdefault(self.LINES, [])
        lines.append((line_number, line_text))

        # Increment counter
        self._count += 1

class TestGrepTree(unittest.TestCase):
    """TODO: This all needs to be implemented."""

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
