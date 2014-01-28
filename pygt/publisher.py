class Publisher(object):
    """Formats a GrepTree in a human readible format and sends to stdout."""
    # Constants
    LINES = 'lines'

    # Templates
    CONTEXT_COLOUR = "\033[93m%s\033[0m"
    LINE_SUM_COLOUR = "\033[91m%d:^\033[0m%s\033[91m$\033[0m"
    CONTEXT_CLEAN = "%s"
    LINE_SUM_CLEAN = "%d:^%s$"

    # Template dicts
    VALID_FORMATS = [
            'colour',
            'clean'
            ]
    LINE_SUM_TEMPS = {
            'colour': LINE_SUM_COLOUR,
            'clean': LINE_SUM_CLEAN
            }
    CONTEXT_TEMPS = {
            'colour': CONTEXT_COLOUR,
            'clean': CONTEXT_CLEAN
            }

    def __init__(self, config):
        self.line_sum_template = ''
        self.context_template = ''
        self.set_format(config.outp_format)

        self.debug = config.debug

    def set_format(self, outp_format):
        """Manipulates various parts of the output template.
        Different foramts can be selected by keyword.
        See `Publisher.VALID_FORMATS`."""
        assert outp_format in self.VALID_FORMATS

        self.line_sum_template = self.LINE_SUM_TEMPS[outp_format]
        self.context_template = self.CONTEXT_TEMPS[outp_format]

    def print_line(self, line_number, line_text, depth):
        """Formats/prints lines."""
        processed = self.line_sum_template % (line_number, line_text)
        print '    '*(depth), processed

    def print_context(self, context, depth):
        """Formats/prints contexts."""
        print '    '*depth + self.context_template % context

    def print_tree(self, tree):
        for key, lines, depth in tree.walk():
            self.print_context(key, depth)
            if lines:
                for line_num, line_txt in lines:
                    self.print_line(line_num, line_txt, depth + 1)
                print

        if self.debug:
            print "Total found: %d" % tree._count
