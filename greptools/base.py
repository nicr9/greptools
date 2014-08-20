"""Core of the package, contains the bootstrapping logic."""
import sys
import json
from argparse import ArgumentParser, RawTextHelpFormatter

from greptools.publisher import (ColouredPublisher,
                            CleanPublisher,
                            FilePublisher,
                            HistPublisher)

def bullet_list(inp):
    """Joins elements in a list into a bullet formatted list."""
    return '\n' + '\n'.join(['- ' + z for z in inp])

class GrepTools(object):
    """Used to bootstrap all greptools CLIs.
    Takes a subclass of `BaseReader` and a list of CLI arguements as params. """
    # CONSTANTS
    DESCRIPTION = '%s Grep Tool.'
    EPILOG = 'Author: Nic Roland\nEmail: nicroland9@gmail.com\nTwitter: @nicr9_'

    VALID_FORMATS = {
            'colour': ColouredPublisher,
            'clean': CleanPublisher,
            'files': FilePublisher,
            'hist': HistPublisher,
            }

    def __init__(self, reader_cls, args):
        self.reader_type = reader_cls.TYPE
        self.reader_cls = reader_cls

        self.config = self.parse_args(args)

        # Disable config.debug if stdout is a pipe
        if not sys.stdout.isatty():
            self.config.debug = False

        if self.config.debug:
            print "=== CLI args ==="
            print args, '\n'
            config_pretty = {x:y for x, y in self.config._get_kwargs()}
            print "=== pygt config ==="
            print json.dumps(config_pretty, indent=4) + '\n'

        self.run()

    def run(self):
        """Execute the search, filter, format, print results."""
        # Either load results from pipe or grep new ones
        if sys.stdin.isatty():
            if self.config.search_term is None:
                sys.exit()
            else:
                reader = self.reader_cls.from_grep(self.config)
        else:
            reader = self.reader_cls.from_pipe(self.config)

            # Set operations
            if self.config.union:
                reader.union()
            elif self.config.diff:
                reader.diff()
            elif self.config.fast_exclude:
                reader.fast_exclude()
            elif self.config.exclude:
                reader.exclude()
            elif self.config.inter:
                reader.inter()
            else:
                reader.fast_inter()

        if self.config.debug:
            print "=== Results dict ==="
            print json.dumps(reader.tree.data, indent=4) + '\n'

        # Push to stdout or dump tree to pipe
        if self.config.force_publish:
            format_ = 'clean' if \
                     self.config.outp_format == 'colour' \
                 else \
                     self.config.outp_format

        if sys.stdout.isatty() or self.config.force_publish:
            publisher = self.VALID_FORMATS[format_]
            pub = publisher(self.config)
            pub.publish(reader.tree)
        else:
            reader.tree.dump(sys.stdout)

    def parse_args(self, argv):
        """For parsing CLI arguements."""
        parser = ArgumentParser(
                formatter_class=RawTextHelpFormatter,
                description=self.DESCRIPTION % self.reader_type,
                epilog=self.EPILOG
                )

        parser.add_argument(
                'search_term',
                default=None,
                nargs='?',
                type=str,
                help='Regex to search for'
                )

        inp_ops = parser.add_argument_group(
                "input arguments",
                "Control which files get searched by default."
                )

        inp_ops.add_argument(
                '-a',
                action='store_true',
                help="Turn file filtering off.",
                dest='no_ignore'
                )

        inp_ops.add_argument(
                '-I',
                default='.gitignore',
                type=str,
                help='File with list of file patterns to ignore.',
                dest='ignore_file'
                )

        inp_ops.add_argument(
                '-i',
                action='store_true',
                help="Turn off case sensitivity.",
                dest='case_off',
                )

        set_ops = parser.add_argument_group(
                "set operations",
                "Used when piping one set of results into an other."
                )

        set_ops.add_argument(
                '-D',
                action='store_true',
                help="XOR results from this search and those piped in.",
                dest='diff',
                )

        set_ops.add_argument(
                '-U',
                action='store_true',
                help="Add the results of this search to those piped in.",
                dest='union',
                )

        set_ops.add_argument(
                '-F',
                action='store_true',
                help="Fast filter results from those piped in.",
                dest='fast_exclude',
                )

        set_ops.add_argument(
                '-E',
                action='store_true',
                help="Slow filter results from those piped in.",
                dest='exclude',
                )

        set_ops.add_argument(
                '-N',
                action='store_true',
                help="Slow intersection with results piped in.",
                dest='inter',
                )

        outp_ops = parser.add_argument_group(
                "output",
                "Control how and what is output to stdout."
                )

        outp_ops.add_argument(
                '-f',
                '--format',
                default='colour',
                type=str,
                help='Format to display output in:%s'
                        % bullet_list(self.VALID_FORMATS),
                dest='outp_format'
                )

        outp_ops.add_argument(
                '-d',
                action='store_true',
                help="Display additional information to aid debugging.",
                dest='debug'
                )

        outp_ops.add_argument(
                '-p',
                action='store_true',
                help="Force non-json output when piping to another process.",
                dest='force_publish'
                )

        return parser.parse_args(argv[1:])
