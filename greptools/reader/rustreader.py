import re
from .reader import BaseReader

class RustReader(BaseReader):
    """An implementation of a Reader for Rust code."""
    # CONSTANTS
    INDENT_RE = re.compile("^(\s*)")
    CONTEXTS_RE = re.compile(r"^\s*(fn|struct|enum)\s([a-zA-Z0-9_:<>]*?)[\s({]")
    TAB = '\t'
    FOUR_SPACES = '    '
    FILE_PATTERNS = ['*.rs']
    TYPE = 'Rust'

    def _find_last_unpaired(self, open_, close_, lines, indx):
        closes = 0
        SIGILS_RE = re.compile("[%s%s]" % (open_, close_))
        for line_no in range(indx-1, -1, -1):
            sigils = re.findall(SIGILS_RE, lines[line_no])
            while sigils:
                s = sigils.pop()
                if s == close_:
                    closes += 1
                elif s == open_:
                    if closes > 0:
                        closes -= 1
                    else:
                        break
            # TODO: This needs a better exit condition
        return line_no, lines[line_no]

    def _strip_line(self, line):
        results = re.search(self.CONTEXTS_RE, line)
        return ' '.join(results.groups())

    def get_context(self, file_path, file_line, tree=None):
        file_indx = file_line - 1

        if tree is None:
            tree = self.tree

        # Create a branch in the tree for this file
        tree.touch(file_path)

        # Get code from file
        lines = self.get_lines(file_path, file_indx)
        assert len(lines) == file_line

        # Determine context
        results = []
        indx = file_indx
        while indx > 0:
            import pdb; pdb.set_trace()
            indx, raw_line = self._find_last_unpaired('{', '}', lines, indx)
            results.append(self._strip_line(raw_line))

        # Add this entry to context tree
        tree.append(
                file_path,
                file_line,
                lines[file_indx].strip('\r\n'),
                reversed(results)
                )
