import sys
import re

from greptools.greptree import GrepTree, count_lines
from greptools.searcher import Searcher

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
    - find_context() : Given the lines of a file and a line index,
            return the context of that line."""

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

    def add_context(self, file_path, file_line, tree=None):
        # Zero-based index for file line number
        file_indx = file_line - 1

        if tree is None:
            tree = self.tree

        # Create a branch in the tree for this file
        tree.touch(file_path)

        lines = self.get_lines(file_path, file_indx)
        assert len(lines) == file_line

        # Add this entry to context tree
        tree.append(
                file_path,
                file_line,
                lines[file_indx].strip('\r\n'),
                self.find_context(lines, file_indx)
                )

    # TODO: The methods below should print comparison tree debug info
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

    def fast_inter(self):
        """Perform intersection on tree using python's re module."""
        to_prune = []
        total_lines = 0
        for keys, lines in self.tree.walk():
            lines = [z for z in lines if re.search(
                                            self.config.search_term,
                                            z[1])
                                            ]
            self.tree.set_lines(keys, lines)
            len_lines = len(lines)
            if len_lines == 0:
                to_prune.append((len(keys), keys))
            else:
                total_lines += len_lines

        for _, keys in sorted(to_prune, reverse=True):
            self.tree.prune(keys)

        self.tree._count = total_lines

    def fast_exclude(self):
        """Filter a tree using python's re module."""
        to_prune = []
        total_lines = 0
        for keys, lines in self.tree.walk():
            lines = [z for z in lines if not re.search(
                                            self.config.search_term,
                                            z[1])
                                            ]
            self.tree.set_lines(keys, lines)
            len_lines = len(lines)
            if len_lines == 0:
                to_prune.append((len(keys), keys))
            else:
                total_lines += len_lines

        for _, keys in sorted(to_prune, reverse=True):
            self.tree.prune(keys)

        self.tree._count = total_lines

    def add_to_tree(self, results, tree=None):
        """Take result and add it to current GrepTree."""
        if tree is None:
            tree = self.tree

        for row in results:
            file_name, file_line, _ = row.split(':')[:3]

            self.add_context(file_name, int(file_line), tree)

    def find_context(self, lines, file_indx):
        """
        Given the lines of a file and the line index, determine the context of that line.
        """
        raise NotImplementedError

class BraceReader(BaseReader):
    """A reader for languages that use braces to inclose code blocks.

    To use this: inherit and implement OPEN_BLOCK, CLOSE_BLOCK, END_LINE,
    _parse_line(), as well as anything needed for implementing BaseReader.
    """
    OPEN_BLOCK = '{'
    CLOSE_BLOCK = '}'
    END_LINE = ';'

    def _scan_file(self, full_text, next_ref):
        results = []
        while True:
            end = self.recursive_rfind(
                    full_text,
                    self.OPEN_BLOCK,
                    self.CLOSE_BLOCK,
                    next_ref
                    )

            start = self.recursive_rfind(
                    full_text,
                    self.all_chars,
                    '',
                    end
                    )

            cntxt = full_text[start:end].strip(self.all_chars)
            if self._line_match(cntxt):
                results.append(self._parse_line(cntxt))
            next_ref = end
            if start == 0:
                break

        return results

    def find_context(self, lines, file_indx):
        self.all_chars = self.CLOSE_BLOCK + self.OPEN_BLOCK + self.END_LINE
        full_text = '\n'.join(lines)
        next_ref = len('\n'.join(lines[:file_indx]))

        results = self._scan_file(full_text, next_ref)

        return reversed(results)

    @staticmethod
    def recursive_rfind(text, find, stepover, end):
        def _rfind(text, exp, find, stepover, start):
            while True:
                # Search
                match = re.search(exp, text[start:])

                case = None
                if match:
                    result = start + match.start() + 1
                    case = match.group(0)

                # Decide what to do next
                if not case:
                    return len(text)
                elif case in find:
                    return result
                elif case in stepover:
                    start = _rfind(text, exp, find, stepover, result)

        exp = r"[%s%s]" % (find, stepover)
        start = len(text) - end
        result = _rfind(''.join(reversed(text)), exp, find, stepover, start)
        return len(text) - result

    def _parse_line(self, line_text):
        raise NotImplementedError
