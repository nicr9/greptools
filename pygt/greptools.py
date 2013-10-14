import sys
import json
from argparse import ArgumentParser, RawTextHelpFormatter

from pygt.publisher import Publisher

def bullet_list(inp):
    return '\n' + '\n'.join(['- ' + z for z in inp])

class GrepTools(object):
    # CONSTANTS
    DESCRIPTION = '%s Grep Tool.'
    EPILOG = 'Author: Nic Roland\nEmail: nicroland9@gmail.com\nTwitter: @nicr9_'

    def __init__(self, reader_cls, args):
        self.reader_type = reader_cls.TYPE

        config = self.parse_args(args)

        # Disable config.debug if stdout is a pipe
        if not sys.stdout.isatty():
            config.debug = False

        if config.debug:
            print "=== CLI args ==="
            print args, '\n'
            config_pretty = {x:y for x, y in config._get_kwargs()}
            print "=== pygt config ==="
            print json.dumps(config_pretty, indent=4) + '\n'

        # Either load results from pipe or grep new ones
        if sys.stdin.isatty():
            if config.search_term is None:
                sys.exit()
            else:
                reader = reader_cls.from_grep(config)
        else:
            reader = reader_cls.from_pipe(config)

            ## Set operations
            #if config.union:
            #    reader.union()
            #elif config.join:
            #    reader.diff()
            #elif config.exclude:
            #    reader.exclude()
            #else:
            #    reader.inter()

        if config.debug:
            print "=== Results dict ==="
            print json.dumps(reader.tree.data, indent=4) + '\n'

        # Push to stdout or dump tree to pipe
        if sys.stdout.isatty():
            publisher = Publisher(config)
            publisher.print_tree(reader.tree)
        else:
            reader.tree.dump(sys.stdout)

    def parse_args(self, argv):
        parser = ArgumentParser(
                formatter_class = RawTextHelpFormatter,
                description = self.DESCRIPTION % self.reader_type,
                epilog = self.EPILOG
                )

        parser.add_argument(
                'search_term',
                default = None,
                nargs='?',
                type = str,
                help = 'Regex to search for'
                )

        parser.add_argument(
                '-f',
                '--format',
                default = 'colour',
                type = str,
                help = 'Format to display output in:%s' 
                        % bullet_list(Publisher.VALID_FORMATS),
                dest = 'outp_format'
                )

        #parser.add_argument(
        #        '-i',
        #        help = "Intersection.",
        #        dest = 'inter',
        #        default = None
        #        )

        #parser.add_argument(
        #        '-U',
        #        help = "Perform a union with the results in file.",
        #        dest = 'union',
        #        default = None
        #        )

        #parser.add_argument(
        #        '-J',
        #        help = "Perform a join with the results in file.",
        #        dest = 'join',
        #        default = None
        #        )

        parser.add_argument(
                '-d',
                action = 'store_true',
                help = "Display additional information to aid debugging.",
                dest = 'debug'
                )

        return parser.parse_args(argv[1:])
