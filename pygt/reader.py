import sys
import re
import subprocess

from pygt.greptree import GrepTree

class BaseReader(object):
    GREP_TEMPLATE = 'grep ./ -Irne "%s" %s'
    INCLUDES_TEMPLATE = '--include="%s"'

    def __init__(self, config):
        self.tree = GrepTree()
        self.outp_path = config.outp_path
        self.debug = config.debug
        self.filter_regex = config.filter_regex

    @classmethod
    def from_file(cls, config):
        temp = cls(config)
        temp.tree = GrepTree.load(config.inp_path)

        return temp

    @classmethod
    def from_grep(cls, config):
        temp = cls(config)
        temp.grep_for(config.search_term)

        return temp

    def perform_union(self, path):
        pass

    def perform_join(self, path):
        pass

    def grep_for(self, exp):
        """
        Execute a grep command to search for the given expression.
        Then print out the context for each result.
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

        for row in results:
            file_name, file_line, line_text = row.split(':')[:3]

            if self.filter_regex and not re.search(self.filter_regex, line_text):
                continue

            self.get_context(file_name, int(file_line))

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

    def _get_indent(self, line):
        """
        Returns the indentation on a line as a substring.
        """
        match = re.match(self.INDENT_RE, line)
        indent = match.group(1)

        return re.sub(self.TAB, self.FOUR_SPACES, indent)

    def get_context(self, file_path, file_line):
        """
        Given the file path and the line number, determine the context of that line.
        """
        # Zero-based index for file line number
        file_indx = file_line - 1

        # Create a branch in the tree for this file
        self.tree.touch(file_path)

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

                    # if line has less indentation add to results, change init_indent
                    if len(next_indent) < len(init_indent):
                        results.append(
                            ' '.join(kw_match.groups())
                            )
                        init_indent = next_indent

        # Add this entry to context tree
        self.tree.append(
                file_path,
                file_line,
                lines[file_indx].strip('\n'),
                reversed(results)
                )
