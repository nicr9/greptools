import sys
import re
import subprocess
import json

class Context(object):
    # CONSTANTS
    INDENT_RE = re.compile("^(\s*)")
    DEF_CLASS_RE = re.compile("^\s*(def|class) (.*?)[(:]")
    TAB = '\t'
    FOUR_SPACES = '    '
    GREP_TEMPLATE = 'grep ./ -Irne "%s" --include="*.py"'
    LINES = 'lines'

    # VARIABLES
    context = {}

    def __init__(self, config):
        self.outp_path = config.outp_path
        self.debug = config.debug
        self.filter_regex = config.filter_regex
        self._num_found = 0

    @classmethod
    def from_file(cls, config):
        temp = cls(config)
        temp.context = cls.load(config.inp_path)

        return temp

    @classmethod
    def from_grep(cls, config):
        temp = cls(config)
        temp.grep_for(config.search_term)

        return temp

    @staticmethod
    def load(path):
        with open(path, 'r') as inp_file:
            return json.load(inp_file)

    def dump(self):
        with open(self.outp_path, 'w') as outp_file:
            flat = json.dumps(self.context, indent=4)
            outp_file.write(flat)

    def perform_union(self, path):
        pass

    def perform_join(self, path):
        pass

    def append(self, file_path, line_number, line_text, cntx_list):
        """
        Adds a line to the context tree.
        """
        # Step through context tree, creating nodes along the way
        pointer = self.context[file_path]
        for step in cntx_list:
            if step not in pointer:
                pointer[step] = {}
            pointer = pointer[step]
        if self.LINES not in pointer:
            pointer[self.LINES] = []

        # Add line_number + line_text to context
        pointer[self.LINES].append((line_number, line_text))
        self._num_found += 1

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
        file_indx = file_line - 1

        # Add file path node to context
        if not file_path in self.context:
            self.context[file_path] = {}

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
        self.append(
                file_path,
                file_line,
                lines[file_indx].strip('\n'),
                reversed(results)
                )

    def grep_for(self, exp):
        """
        Execute a grep command to search for the given expression.
        Then print out the context for each result.
        """
        results = []
        try:
            response = subprocess.check_output(
                    [self.GREP_TEMPLATE % exp],
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
