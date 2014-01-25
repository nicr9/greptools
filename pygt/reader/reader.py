import sys

from pygt.greptree import GrepTree, count_lines
from pygt.searcher import Searcher

def warn(msg):
    """Print message in a warning header."""
    print "=== \033[91mWarn: %s\033[0m ===\n" % str(msg)

def set_op(a_subtree, b_subtree, func1, func2):
    """Convienience function for performing a set operation on two sub trees."""
    # Using a closure as a counter is difficult so we'll sum a list instead
    count = []

    def _set_op(a_subtree, b_subtree, func1, func2):
        """Recursive function for performing set operations."""
        a_nodes = set(a_subtree.keys())
        b_nodes = set(b_subtree.keys())

        floor = {}
        for node in func1(a_nodes, b_nodes):
            if node == 'lines':
                a_set = set(tuple(z) for z in a_subtree.get(node, []))
                b_set = set(tuple(z) for z in b_subtree.get(node, []))

                temp = func2(a_set, b_set)
                count.append(len(temp))
                if temp != []:
                    floor[node] = temp

            else:
                a_branch = a_subtree.get(node, {})
                b_branch = b_subtree.get(node, {})

                if not a_branch and b_branch:
                    temp = a_branch if a_branch else b_branch
                    count.append(count_lines(temp))
                else:
                    temp = _set_op(a_branch, b_branch, func1, func2)

                if temp != {}:
                    floor[node] = temp

        return floor

    return _set_op(a_subtree, b_subtree, func1, func2), sum(count)

class BaseReader(object):
    """Base class only. Please subclass and implement the following:

    - FILE_PATTERNS : a list of file extensions to pass to Searcher.
    - TYPE : The name of the programming language this Reader specialises in
    - get_context() : Given a file and line number,
                        this should return the lines context."""

    # Things that should be defined by subclass
    FILE_PATTERNS = []
    TYPE = ''

    def __init__(self, config):
        self.tree = GrepTree()
        self.config = config
        self.debug = config.debug

    @classmethod
    def from_file(cls, config, path):
        """Create Reader and populate tree from file."""
        temp = cls(config)
        temp.tree = GrepTree.load_path(path)

        return temp

    @classmethod
    def from_grep(cls, config):
        """Create Reader and populate tree by grepping files."""
        temp = cls(config)
        temp.tree = temp.build_tree(config.search_term)

        return temp

    @classmethod
    def from_pipe(cls, config):
        """Create Reader and read tree from incomming pipe."""
        temp = cls(config)
        try:
            temp.tree = GrepTree.load(sys.stdin)
        except ValueError:
            if temp.debug:
                warn("Choked on input from pipe")
            temp.tree = GrepTree()

        return temp

    @staticmethod
    def get_lines(file_path, file_indx):
        """Returns lines in a file leading upto a certain line (inclusive)."""
        # Read in all lines up to and including the line given
        lines = []
        with open(file_path) as file_:
            for i, line in enumerate(file_):
                if i <= file_indx:
                    lines.append(line)
                else:
                    break

        return lines

    def build_tree(self, query):
        """Perform grep search and sort results into GrepTree."""
        # Grep for expresion
        searcher = Searcher(self.config, self.FILE_PATTERNS)
        results = searcher.grep_for(query)

        # Create a temp tree and add all results to tree
        tree = GrepTree()
        self.add_to_tree(results, tree)

        return tree

    # TODO: The methods below should print additional debug info of the comparison tree

    def union(self):
        """Perform union set operation against GrepTree piped in."""
        tree = self.build_tree(self.config.search_term)

        func1 = lambda a, b: a | b
        func2 = lambda a, b: list(a | b)

        self.tree.data, self.tree._count = set_op(
                self.tree.data,
                tree.data,
                func1,
                func2
                )

    def diff(self):
        """Perform XOR set operation against GrepTree piped in."""
        tree = self.build_tree(self.config.search_term)

        func1 = lambda a, b: a | b
        func2 = lambda a, b: list(a ^ b)

        self.tree.data, self.tree._count = set_op(
                self.tree.data,
                tree.data,
                func1,
                func2
                )

    def exclude(self):
        """Filter results piped in from those in current GrepTree"""
        tree = self.build_tree(self.config.search_term)

        func1 = lambda a, b: a
        func2 = lambda a, b: list(a - b)

        self.tree.data, self.tree._count = set_op(
                self.tree.data,
                tree.data,
                func1,
                func2
                )

    def inter(self):
        """Perform intersection set operation against GrepTree piped in."""
        tree = self.build_tree(self.config.search_term)

        func1 = lambda a, b: a & b
        func2 = lambda a, b: list(a & b)

        self.tree.data, self.tree._count = set_op(
                self.tree.data,
                tree.data,
                func1,
                func2
                )

    def add_to_tree(self, results, tree=None):
        """Take result and add it to current GrepTree."""
        if tree is None:
            tree = self.tree

        for row in results:
            file_name, file_line, _ = row.split(':')[:3]

            self.get_context(file_name, int(file_line), tree)

    def get_context(self, file_path, file_line, tree=None):
        """
        Given the file path and the line number, determine the context of that line.
        """
        raise NotImplementedError
