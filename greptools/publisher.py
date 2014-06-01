from greptools.greptree import count_lines

def margin_vals(d):
    max_len = max([len(key) for key in d.values()])
    return {k: v + ' ' * (max_len - len(v)) for k, v in d.iteritems()}

class BasePublisher(object):
    """Formats a GrepTree in a human readible format and sends to stdout."""
    # Constants
    LINES = 'lines'
    BREAK_AFTER_LINES = True

    def __init__(self, config):
        self.debug = config.debug

    def print_line(self, line_number, line_text, depth):
        """Formats/prints lines."""
        raise NotImplementedError

    def print_context(self, context, depth):
        """Formats/prints contexts."""
        raise NotImplementedError

    def publish(self, tree):
        """Print out information about a tree."""
        for keys, lines in tree.walk():
            tail = keys[-1]
            depth = len(keys) - 1
            self.print_context(tail, depth)
            if lines:
                for line_num, line_txt in lines:
                    self.print_line(line_num, line_txt, depth)
                if self.BREAK_AFTER_LINES:
                    print

        if self.debug:
            print "Total found: %d" % tree._count

class ColouredPublisher(BasePublisher):
    CONTEXT_TEMPLATE = "\033[93m%s\033[0m"
    LINE_TEMPLATE = "\033[91m%d:^\033[0m%s\033[91m$\033[0m"

    def print_line(self, line_number, line_text, depth):
        processed = self.LINE_TEMPLATE % (line_number, line_text)
        print '    '*(depth + 1), processed

    def print_context(self, context, depth):
        print '    '*depth + self.CONTEXT_TEMPLATE % context

class CleanPublisher(BasePublisher):
    CONTEXT_TEMPLATE = "%s"
    LINE_TEMPLATE = "%d:^%s$"

    def print_line(self, line_number, line_text, depth):
        processed = self.LINE_TEMPLATE % (line_number, line_text)
        print '    '*(depth + 1), processed

    def print_context(self, context, depth):
        print '    '*depth + self.CONTEXT_TEMPLATE % context

class FilePublisher(BasePublisher):
    CONTEXT_TEMPLATE = "%s"
    BREAK_AFTER_LINES = False

    def print_line(self, line_number, line_text, depth):
        pass

    def print_context(self, context, depth):
        if depth == 0:
            print self.CONTEXT_TEMPLATE % context

class HistPublisher(BasePublisher):
    def publish(self, tree):
        root_keys = {key: key for key in tree.data.keys()}
        m_keys = margin_vals(root_keys)
        item_counts = {}
        for key in root_keys:
            st = tree.touch(key)
            count = count_lines(st)
            item_counts[key] = count
            m_keys[key] += ' ' + str(count)

        for key, val in margin_vals(m_keys).iteritems():
            print val, '#' * item_counts[key]
