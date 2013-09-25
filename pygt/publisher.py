class Publisher(object):
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
        self.set_format(config.outp_format)
        self.debug = config.debug

    def set_format(self, outp_format):
        assert outp_format in self.VALID_FORMATS

        self.line_sum_template = self.LINE_SUM_TEMPS[outp_format]
        self.context_template = self.CONTEXT_TEMPS[outp_format]

    def _format_line(self, line_number, line_text):
        return self.line_sum_template % (line_number, line_text)

    def print_tree(self, tree):
        def _print(data, counter=0):
            for key, val in data.iteritems():
                if isinstance(val, dict):
                    print ' '*counter + self.context_template % key
                    if self.LINES in val:
                        for row in val[self.LINES]:
                            processed_row = self._format_line(*row)
                            print ' '*(counter+4), processed_row
                        print
                    _print(val, counter+4)
                elif isinstance(val, list):
                    pass
                elif isinstance(val, str):
                        print ' '*counter, val
                else:
                    print "%s type found: %s" % (type(val), val)

        _print(tree.data)

        if self.debug:
            print "Total found: %d" % tree._count
