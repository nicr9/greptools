class BasePublisher(object):
    """Formats a GrepTree in a human readible format and sends to stdout."""
    # Constants
    LINES = 'lines'

    def __init__(self, config):
        self.debug = config.debug

    def print_line(self, line_number, line_text, depth):
        raise NotImplementedError

    def print_context(self, context, depth):
        raise NotImplementedError

    def print_tree(self, tree):
        for key, lines, depth in tree.walk():
            self.print_context(key, depth)
            if lines:
                for line_num, line_txt in lines:
                    self.print_line(line_num, line_txt, depth + 1)
                print

        if self.debug:
            print "Total found: %d" % tree._count

class ColouredPublisher(BasePublisher):
    CONTEXT_TEMPLATE = "\033[93m%s\033[0m"
    LINE_TEMPLATE = "\033[91m%d:^\033[0m%s\033[91m$\033[0m"

    def print_line(self, line_number, line_text, depth):
        """Formats/prints lines."""
        processed = self.LINE_TEMPLATE % (line_number, line_text)
        print '    '*(depth), processed

    def print_context(self, context, depth):
        """Formats/prints contexts."""
        print '    '*depth + self.CONTEXT_TEMPLATE % context

class CleanPublisher(BasePublisher):
    CONTEXT_TEMPLATE = "%s"
    LINE_TEMPLATE = "%d:^%s$"

    def print_line(self, line_number, line_text, depth):
        """Formats/prints lines."""
        processed = self.LINE_TEMPLATE % (line_number, line_text)
        print '    '*(depth), processed

    def print_context(self, context, depth):
        """Formats/prints contexts."""
        print '    '*depth + self.CONTEXT_TEMPLATE % context
