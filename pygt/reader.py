import sys
import re
import subprocess

from pygt.greptree import GrepTree

# TODO: Considder moving this to GrepTree module
def count_lines(subtree):
    count = 0
    for key, val in subtree.iteritems():
        if key == 'lines':
            count += len(val)
        else:
            count += count_lines(val)

    return count

class BaseReader(object):
    GREP_TEMPLATE = 'grep ./ -Irne "%s" %s'
    INCLUDES_TEMPLATE = '--include="%s"'

    def __init__(self, config):
        self.tree = GrepTree()
        self.config = config
        self.debug = config.debug

    @classmethod
    def from_file(cls, config, path):
        temp = cls(config)
        temp.tree = GrepTree.load_path(path)

        return temp

    @classmethod
    def from_grep(cls, config):
        temp = cls(config)
        temp.tree = temp.build_tree(config.search_term)

        return temp

    @classmethod
    def from_pipe(cls, config):
        temp = cls(config)
        temp.tree = GrepTree.load(sys.stdin)

        return temp

    def build_tree(self, query):
        # Grep for expresion
        results = self.grep_for(query)

        # Create a temp tree and add all results to tree
        tree = GrepTree()
        self.add_to_tree(results, tree)

        return tree

    # TODO: The methods below should print additional debug info of the comparison tree

    def union(self):
        tree = self.build_tree(self.config.search_term)
        self._perform_union(tree)

    def diff(self):
        tree = self.build_tree(self.config.search_term)
        self._perform_diff(tree)

    def exclude(self):
        tree = self.build_tree(self.config.search_term)
        self._perform_exclude(tree)

    def inter(self):
        tree = self.build_tree(self.config.search_term)
        self._perform_inter(tree)

    def _perform_union(self, tree):
        # Using a closure as a counter is difficult so we'll sum a list instead
        count = []

        def _pu(a, b):
            a_nodes = set(a.keys())
            b_nodes = set(b.keys())

            floor = {}
            for node in a_nodes | b_nodes:
                if node == 'lines':
                    a_set = set(tuple(z) for z in a.get(node, []))
                    b_set = set(tuple(z) for z in b.get(node, []))
                    temp = list(a_set | b_set)
                    count.append(len(temp))
                    if temp != []:
                        floor[node] = temp

                else:
                    a_branch = a.get(node, {})
                    b_branch = b.get(node, {})

                    if not a_branch and b_branch:
                        temp = a_branch if a_branch else b_branch
                        count.append(count_lines(temp))
                    else:
                        temp = _pu(a_branch, b_branch)

                    if temp != {}:
                        floor[node] = temp

            return floor

        self.tree.data = _pu(self.tree.data, tree.data)
        self.tree._count = sum(count)

    def _perform_diff(self, tree):
        # Using a closure as a counter is difficult so we'll sum a list instead
        count = []

        def _pd(a, b):
            a_nodes = set(a.keys())
            b_nodes = set(b.keys())

            floor = {}
            for node in a_nodes | b_nodes:
                if node == 'lines':
                    a_set = set(tuple(z) for z in a.get(node, []))
                    b_set = set(tuple(z) for z in b.get(node, []))
                    temp = list(a_set ^ b_set)
                    count.append(len(temp))
                    if temp != []:
                        floor[node] = temp
                else:
                    temp = _pd(a.get(node, {}), b.get(node, {}))
                    if temp != {}:
                        floor[node] = temp

            return floor

        self.tree.data = _pd(self.tree.data, tree.data)
        self.tree._count = sum(count)

    def _perform_exclude(self, tree):
        # Using a closure as a counter is difficult so we'll sum a list instead
        count = []

        def _pe(a, b):
            a_nodes = set(a.keys())
            b_nodes = set(b.keys())

            floor = {}
            for node in a_nodes:
                if node == 'lines':
                    a_set = set(tuple(z) for z in a[node])
                    b_set = set(tuple(z) for z in b.get(node, []))
                    temp = list(a_set - b_set)
                    count.append(len(temp))
                    if temp != []:
                        floor[node] = temp
                else:
                    temp = _pe(a[node], b.get(node, {}))
                    if temp != {}:
                        floor[node] = temp

            return floor

        self.tree.data = _pe(self.tree.data, tree.data)
        self.tree._count = sum(count)

    def _perform_inter(self, tree):
        # Using a closure as a counter is difficult so we'll sum a list instead
        count = []

        def _pi(a, b):
            a_nodes = set(a.keys())
            b_nodes = set(b.keys())

            floor = {}
            for node in a_nodes & b_nodes:
                if node == 'lines':
                    a_set = set(tuple(z) for z in a[node])
                    b_set = set(tuple(z) for z in b[node])
                    temp = list(a_set & b_set)
                    count.append(len(temp))
                    if temp != []:
                        floor[node] = temp
                else:
                    temp = _pi(a[node], b[node])
                    if temp != {}:
                        floor[node] = temp

            return floor

        self.tree.data = _pi(self.tree.data, tree.data)
        self.tree._count = sum(count)

    def grep_for(self, exp):
        """
        Execute a grep command to search for the given expression.
        Then add each result to self.tree.
        """
        results = []
        try:
            response = subprocess.check_output(
                    [self._grep_cmd(exp, self.FILE_PATTERNS)],
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
        if tree is None:
            tree = self.tree

        for row in results:
            file_name, file_line, line_text = row.split(':')[:3]

            self.get_context(file_name, int(file_line), tree)

    def _grep_cmd(self, exp, file_patterns):
        inclds = ' '.join([self.INCLUDES_TEMPLATE % z for z in file_patterns])
        return self.GREP_TEMPLATE % (exp, inclds)

class PythonReader(BaseReader):
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
        """
        Given the file path and the line number, determine the context of that line.
        """
        # Zero-based index for file line number
        file_indx = file_line - 1

        if tree is None:
            tree = self.tree

        # Create a branch in the tree for this file
        tree.touch(file_path) #TODO:

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
                # Ignore lines that aren't a function or a class
                kw_match = re.search(self.DEF_CLASS_RE, lines[line_no])
                if kw_match:
                    # Get indent of relevant lines
                    next_indent = self._get_indent(lines[line_no])

                    # if line has less indentation add to results
                    # then change init_indent
                    if len(next_indent) < len(init_indent):
                        results.append(
                            ' '.join(kw_match.groups())
                            )
                        init_indent = next_indent

        # Add this entry to context tree
        tree.append(
                file_path,
                file_line,
                lines[file_indx].strip('\n'),
                reversed(results)
                )
