import re
from .reader import BaseReader

class IndentReader(BaseReader):
    TAB = '\t'
    FOUR_SPACES = '    '

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

        lines = self.get_lines(file_path, file_indx)
        assert len(lines) == file_line

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

        # Add this entry to context tree
        tree.append(
                file_path,
                file_line,
                lines[file_indx].strip('\r\n'),
                reversed(results)
                )


class PythonReader(IndentReader):
    """An implementation of a Reader for Python code."""
    # CONSTANTS
    INDENT_RE = re.compile("^(\s*)")
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
