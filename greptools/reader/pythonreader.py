import re
from .reader import BaseReader

class IndentReader(BaseReader):
    INDENT_RE = re.compile("^(\s*)")
    TAB = '\t'
    FOUR_SPACES = '    '

    def _get_indent(self, line):
        """
        Returns the indentation on a line as a substring.
        """
        match = re.match(self.INDENT_RE, line)
        indent = match.group(1)

        return re.sub(self.TAB, self.FOUR_SPACES, indent)

    def find_context(self, lines, file_indx):
        # Get indent of specified line
        init_indent = self._get_indent(lines[file_indx])

        results = []
        for line_no in range(file_indx-1, -1, -1):
            # Ignore empty lines
            if lines[line_no].strip('\r\n'):
                # Get indent of relevant lines
                next_indent = self._get_indent(lines[line_no])

                # if line has less indentation
                if len(next_indent) < len(init_indent):
                    # Ignore lines that aren't a function or a class
                    if self._line_match(lines[line_no]):
                        # add to results
                        results.append(
                            self._parse_line(lines[line_no])
                            )

                    # then change init_indent
                    init_indent = next_indent

        return reversed(results)

class PythonReader(IndentReader):
    """An implementation of a Reader for Python code."""
    # CONSTANTS
    DEF_CLASS_RE = re.compile("^\s*(def|class) (.*?)[(:]")
    FILE_PATTERNS = ['*.py']
    TYPE = 'Python'

    def _line_match(self, line_text):
        if re.search(self.DEF_CLASS_RE, line_text):
            return True
        else:
            return False

    def _parse_line(self, line_text):
        match = re.search(self.DEF_CLASS_RE, line_text)
        return ' '.join(match.groups())
