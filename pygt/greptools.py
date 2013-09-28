import sys
import json
from argparse import ArgumentParser, FileType, RawTextHelpFormatter

from pygt.publisher import Publisher

class GrepTools(object):
    # CONSTANTS
    DESCRIPTION = '%s Grep Tool.'
    EPILOG = 'Author: Nic Roland\nEmail: nicroland9@gmail.com\nTwitter: @nicr9_'

    def __init__(self, reader_cls, args):
        self.reader_type = reader_cls.TYPE

        config = self.parse_args(args)

        if config.debug:
            print "=== CLI args ==="
            print args, '\n'
            config_pretty = {x:y for x, y in config._get_kwargs()}
            print "=== pygt config ==="
            print json.dumps(config_pretty, indent=4) + '\n'

        # Either load results or grep new ones
        if config.inp_path:
            reader = reader_cls.from_file(config)
        else:
            reader = reader_cls.from_grep(config)

        ## Set operations
        #if config.union:
        #    self.perform_union(config.union)
        #elif config.join:
        #    self.perform_join(config.join)

        # Save to file or push to stdout
        if config.outp_path:
            reader.tree.dump(outp_path)
        else:
            publisher = Publisher(config)
            publisher.print_tree(reader.tree)

    def _arg_desc_list(self, inp):
        return '\n' + '\n'.join(['- ' + z for z in inp])

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
                        % self._arg_desc_list(Publisher.VALID_FORMATS),
                dest = 'outp_format'
                )

        parser.add_argument(
                '-o',
                '--outp',
                type = str,
                help = 'Save results to file',
                dest = 'outp_path',
                default = None
                )

        parser.add_argument(
                '-i',
                '--inp',
                type = str,
                help = 'Load results from file',
                dest = 'inp_path',
                default = None
                )

        parser.add_argument(
                '-F',
                help = "Filter resultng lines by regex",
                dest = 'filter_regex',
                default = None
                )

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
