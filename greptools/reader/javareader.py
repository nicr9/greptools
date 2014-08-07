import re
from .reader import BraceReader

class JavaReader(BraceReader):
    """An implementation of a Reader for Java code."""
    # CONSTANTS
    CLASS_RE = re.compile("class (.*?)\s*[\n{]")
    x = "(abstract|static|final|strictfp|private|protected|public)*\s*class\s*(.*?)\s*{"
    FILE_PATTERNS = ['*.java']
    TYPE = 'Java'

    def _line_match(self, line_text):
        if re.search(self.CLASS_RE, line_text):
            return True
        else:
            return False

    def _parse_line(self, line_text):
        return line_text.strip()
