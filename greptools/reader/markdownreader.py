import re
from .reader import BaseReader

class MarkdownReader(BaseReader):
    """An implementation of a Reader for Markdown files."""
    # CONSTANTS
    HEADER_RE = re.compile("^(#+)")
    FILE_PATTERNS = ['*.md']
    TYPE = 'Markdown'

    def _get_last_header(self, lines, indx):
        """
        Returns the indentation on a line as a substring.
        """
        for line_no in range(indx-1, -1, -1):
            depth = self._get_header_depth(lines, line_no)
            if depth:
                yield depth, line_no

    def _get_header_depth(self, lines, indx):
            match = re.match(self.HEADER_RE, lines[indx])
            if match:
                return len(match.group(1))

    def find_context(self, lines, file_indx):
        # Recursively trace headers of file
        init_depth = self._get_header_depth(lines, file_indx)
        results = []
        for depth, indx in self._get_last_header(lines, file_indx):
            if depth < init_depth or init_depth is None:
                results.append(lines[indx].strip())
                init_depth = depth

        return reversed(results)
