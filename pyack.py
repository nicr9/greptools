#! /usr/bin/python2.7
import sys
import re
import subprocess

class Context(object):

    # CONSTANTS
    USAGE = """python2.7 %s <file> <line number>""" % __file__
    INDENT_RE = "^(\s*)"
    DEF_CLASS_RE = "^\s*(def|class) (.*?)[(:]"
    CONTEXT_COLOUR = "\033[93m%s\033[0m"
    LINE_SUM_COLOUR = "\033[91m%d:^\033[0m%s\033[91m$\033[0m\n"
    TAB = '\t'
    FOUR_SPACES = '    '
    GREP_TEMPLATE = 'grep ./ -Irne "%s" --include="*.py"'

    def __init__(self, args):
        if len(args) == 3:
            file_path = args[1]
            file_line = int(args[2])

            context = self.find_context(file_path, file_line)
            self.print_context(context)
        elif len(args) == 2:
            self.grep_for(args[1])
        else:
            print self.USAGE

    def get_indent(self, line):
        """
        Get the indentation on a line as a substring.
        """
        match = re.match(self.INDENT_RE, line)
        indent = match.group(1)

        return re.sub(self.TAB, self.FOUR_SPACES, indent)

    def find_context(self, file_path, file_line):
        file_indx = file_line - 1

        # Get all lines up to and including the line given
        lines = []
        with open(file_path) as file_:
            for i, line in enumerate(file_):
                if i <= file_indx:
                    lines.append(line)
                else:
                    break

        assert len(lines) == file_line
        init_indent = self.get_indent(lines[file_indx])

        results = [(file_path, file_line, lines[file_indx], None)]
        for line_no in range(file_indx-1, -1, -1):
            if lines[line_no].strip():
                kw_match = re.search(self.DEF_CLASS_RE, lines[line_no])
                if kw_match:
                    next_indent = self.get_indent(lines[line_no])

                    if len(next_indent) < len(init_indent):
                        results.append((
                            file_path,
                            line_no + 1,
                            lines[line_no],
                            ' '.join(kw_match.groups())
                            ))
                        init_indent = next_indent

        return results

    def print_context(self, results):
        """
        Print out the context (e.g. file => class => method).
        Then print out line_number:^line_text$.
        """
        cont_list = [results[0][0]] + [z[3].strip() for z in reversed(results[1:])]
        cont = " => ".join(cont_list)

        print self.CONTEXT_COLOUR % cont
        print self.LINE_SUM_COLOUR % (results[0][1], results[0][2].strip())

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

            context = self.find_context(file_name, int(file_line))
            self.print_context(context)

if __name__ == "__main__":
    x = Context(sys.argv)
