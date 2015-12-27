import re
from .reader import BraceReader

class GoReader(BraceReader):
    """An implementation of a Reader for Go code."""
    # CONSTANTS
    # two or more of these because attrs are always followed by some whitespace
    ALL_ATTRS = "(type|func)\s*"
    CLASS_FUNC_RE = re.compile(
            ALL_ATTRS +
            "([a-zA-Z0-9_()\s]+)\s*"
            )
    FILE_PATTERNS = ['*.go']
    TYPE = 'Go'

    def _line_match(self, line_text):
        if re.search(self.CLASS_FUNC_RE, line_text):
            return True
        else:
            return False

    def _parse_line(self, line_text):
        components = [z.strip() for z in re.split('[\n\r]', line_text)]
        reconstructed = [z for z in components if z][-1]
        return reconstructed
