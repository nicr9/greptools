#! /usr/bin/python2.7
import sys
import re
import subprocess
import json

class Context(object):
    # CONSTANTS
    USAGE = """python2.7 %s <file> <line number>""" % __file__
    INDENT_RE = "^(\s*)"
    DEF_CLASS_RE = "^\s*(def|class) (.*?)[(:]"
    CONTEXT_COLOUR = "\033[93m%s\033[0m"
    LINE_SUM_COLOUR = "\033[91m%d:^\033[0m%s\033[91m$\033[0m"
    TAB = '\t'
    FOUR_SPACES = '    '
    GREP_TEMPLATE = 'grep ./ -Irne "%s" --include="*.py"'
    LINES = 'lines'

    # VARIABLES
    context = {}

    def __init__(self, args):
        if len(args) == 3:
            file_path = args[1]
            file_line = int(args[2])

            self.get_context(file_path, file_line)
            self.print_dict(self.context)
        elif len(args) == 2:
            self.grep_for(args[1])
        else:
            print self.USAGE

    def add_context(self, cntx_list):
        """
        Adds a node to the context tree.
        """
        pointer = self.context[cntx_list[0]]
        for step in cntx_list[1:-1]:
            if step not in pointer:
                pointer[step] = {}
            pointer = pointer[step]
        if self.LINES not in pointer:
            pointer[self.LINES] = []
        pointer[self.LINES].append(cntx_list[-1])

    def get_indent(self, line):
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

        # Get all lines up to and including the line given
        lines = []
        with open(file_path) as file_:
            for i, line in enumerate(file_):
                if i <= file_indx:
                    lines.append(line)
                else:
                    break
        assert len(lines) == file_line

        # Get indent of specified line
        init_indent = self.get_indent(lines[file_indx])

        results = [self.LINE_SUM_COLOUR % (file_line, lines[file_indx].strip('\n'))]
        for line_no in range(file_indx-1, -1, -1):
            # Ignore empty lines
            if lines[line_no].strip():
                # Ignore lines that aren't a function or a class
                kw_match = re.search(self.DEF_CLASS_RE, lines[line_no])
                if kw_match:
                    # Get indent of relevant lines
                    next_indent = self.get_indent(lines[line_no])

                    # if line has less indentation add to results, change init_indent
                    if len(next_indent) < len(init_indent):
                        results.append(
                            ' '.join(kw_match.groups())
                            )
                        init_indent = next_indent

        # Each context entry should also contain file path
        results.append(file_path)
        results = list(reversed(results))

        self.add_context(results)

    def print_dict(self, obj, counter=0):
        for key, val in obj.iteritems():
            if isinstance(val, dict):
                print ' '*counter + self.CONTEXT_COLOUR % key
                if self.LINES in val:
                    for row in val[self.LINES]:
                        print ' '*(counter+4), row
                    print
                self.print_dict(val, counter+4)
            elif isinstance(val, list):
                #for row in val:
                 #   print ' '*counter, row
                pass
            elif isinstance(val, str):
                print ' '*counter, val
            else:
                print "%s type found: %s" % (type(val), val)

    def grep_for(self, exp):
        """
        Execute a grep command to search for the given expression.
        Then print out the context for each result.
        """
        results = subprocess.check_output(
                [self.GREP_TEMPLATE % exp],
                shell=True
                )

        for row in results.splitlines(False):
            file_name, file_line = row.split(':')[:2]

            self.get_context(file_name, int(file_line))
        self.print_dict(self.context)

if __name__ == "__main__":
    x = Context(sys.argv)
