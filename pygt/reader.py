import sys
import re
import subprocess
import os.path

from fnmatch import filter as fnfilter
from os import walk, getcwd

from pygt.greptree import GrepTree, count_lines

def glob_recursive(ptrn):
    """Returns a list of paths under ./ that match a given glob pattern."""
    ptrn = ptrn[:-1] if ptrn[-1] == '/' else ptrn

    dir_matches = []
    file_matches = []
    for root, dirnames, filenames in walk(getcwd()):
        for dirname in fnfilter(dirnames, ptrn):
            dir_matches.append(os.path.relpath(os.path.join(root, dirname)))
        for filename in fnfilter(filenames, ptrn):
            file_matches.append(os.path.join(root, filename))

    return dir_matches, file_matches

def set_op(a_subtree, b_subtree, func1, func2):
    """Convienience function for performing a set operation on two sub trees."""
    # Using a closure as a counter is difficult so we'll sum a list instead
    count = []

    def _set_op(a_subtree, b_subtree, func1, func2):
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

    - FILE_PATTERNS : a list of file extensions to read.
    - TYPE : The name of the programming language this Reader pertains to
    - get_context() : Given a file and line number,
                        this should return the lines context."""

    GREP_TEMPLATE = 'grep ./ -Irne "%s"%s%s'
    INCLUDES_TEMPLATE = ' --include="%s"'
    EXCLUDES_TEMPLATE = ' --exclude-dir="%s" --exclude="%s"'

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
        temp.tree = GrepTree.load(sys.stdin)

        return temp

    def build_tree(self, query):
        """Perform grep search and sort results into GrepTree."""
        # Grep for expresion
        results = self.grep_for(query)

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

    def _get_exclds(self):
        """Decide which file should be used to build list of paths to ignore."""
        if not self.config.no_ignore:
            return self.config.ignore_file

    def grep_for(self, exp):
        """
        Execute a grep command to search for the given expression.
        Then add each result to self.tree.
        """
        results = []
        exclds = self._get_exclds()
        try:
            response = subprocess.check_output(
                    [self._grep_cmd(exp, self.FILE_PATTERNS, exclds)],
                    shell=True
                    )
            results = response.splitlines()

            if self.debug:
                print "=== Grep results ==="
                print response, "Total results: %d\n" % len(results)
        except subprocess.CalledProcessError, e:
            if e.returncode == 1:
                print "Couldn't find anything matching '%s'" % exp
            else:
                print "Whoops, grep returned errorcode %d" % e.errorcode
            sys.exit()

        return results

    def add_to_tree(self, results, tree=None):
        """Take result and add it to current GrepTree."""
        if tree is None:
            tree = self.tree

        for row in results:
            file_name, file_line, _ = row.split(':')[:3]

            self.get_context(file_name, int(file_line), tree)

    def _grep_cmd(self, exp, file_patterns, exclude_from=None):
        """Build the grep command used to perform search."""
        excld_flags = ''
        if exclude_from:
            exclds = set()
            excld_dirs = set()
            with open(exclude_from, 'r') as inp:
                for row in inp:
                    dirs, files = glob_recursive(row.strip())
                    excld_dirs.update(dirs)
                    exclds.update(files)

            excld_dirs = '" --exclude-dir="'.join(excld_dirs)
            exclds = '" --exclude="'.join(exclds)

            excld_flags = self.EXCLUDES_TEMPLATE % (excld_dirs, exclds)

        inclds = ' '.join([self.INCLUDES_TEMPLATE % z for z in file_patterns])
        return self.GREP_TEMPLATE % (exp, excld_flags, inclds)

    def get_context(self, file_path, file_line, tree=None):
        """
        Given the file path and the line number, determine the context of that line.
        """
        raise NotImplementedError

class PythonReader(BaseReader):
    """An implementation of a Reader for Python code."""
    # CONSTANTS
    INDENT_RE = re.compile("^(\s*)")
    DEF_CLASS_RE = re.compile("^\s*(def|class) (.*?)[(:]")
    TAB = '\t'
    FOUR_SPACES = '    '
    FILE_PATTERNS = ['*.py']
    TYPE = 'Python'

    def _get_indent(self, line):
        """
        Returns the indentation on a line as a substring.
        """
        match = re.match(self.INDENT_RE, line)
        indent = match.group(1)

        return re.sub(self.TAB, self.FOUR_SPACES, indent)

    def get_context(self, file_path, file_line, tree=None):
        # Zero-based index for file line number
        file_indx = file_line - 1

        if tree is None:
            tree = self.tree

        # Create a branch in the tree for this file
        tree.touch(file_path)

        # Read in all lines up to and including the line given
        lines = []
        with open(file_path) as file_:
            for i, line in enumerate(file_):
                if i <= file_indx:
                    lines.append(line)
                else:
                    break
        assert len(lines) == file_line

        # Get indent of specified line
        init_indent = self._get_indent(lines[file_indx])

        results = []
        for line_no in range(file_indx-1, -1, -1):
            # Ignore empty lines
            if lines[line_no].strip():
                # Get indent of relevant lines
                next_indent = self._get_indent(lines[line_no])

                # if line has less indentation 
                if len(next_indent) < len(init_indent):
                    # Ignore lines that aren't a function or a class
                    kw_match = re.search(self.DEF_CLASS_RE, lines[line_no])
                    if kw_match:
                        # add to results
                        results.append(
                            ' '.join(kw_match.groups())
                            )

                    # then change init_indent
                    init_indent = next_indent

        # Add this entry to context tree
        tree.append(
                file_path,
                file_line,
                lines[file_indx].strip('\n'),
                reversed(results)
                )
