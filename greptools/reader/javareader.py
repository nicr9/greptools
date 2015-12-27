import re
from .reader import BraceReader, replace_parens

class JavaReader(BraceReader):
    """An implementation of a Reader for Java code."""
    # CONSTANTS
    # two or more of these because attrs are always followed by some whitespace
    ALL_ATTRS = "(abstract|static|final|strictfp|private|protected|public|class|\s+){2,}"
    CLASS_FUNC_RE = re.compile(
            ALL_ATTRS +
            "([a-zA-Z0-9_]+)\s*"
            )
    FILE_PATTERNS = ['*.java']
    TYPE = 'Java'

    def _line_match(self, line_text):
        if re.search(self.CLASS_FUNC_RE, line_text):
            return True
        else:
            return False

    def _parse_line(self, line_text):
        components = [z.strip() for z in re.split('[\n\r]', line_text)]
        reconstructed = [z for z in components if z][-1]
        return replace_parens(reconstructed)
