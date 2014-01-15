import subprocess
import os.path

from fnmatch import filter as fnfilter
from os import walk, getcwd

def glob_recursive(ptrn):
    """Returns a list of paths under ./ that match a given glob pattern."""
    ptrn = ptrn[:-1] if ptrn[-1] == '/' else ptrn

    dir_matches = []
    file_matches = []
    for root, dirnames, filenames in walk(getcwd()):
        for dirname in fnfilter(dirnames, ptrn):
            dir_matches.append(os.path.relpath(os.path.join(root, dirname)))
        for filename in fnfilter(filenames, ptrn):
            file_matches.append(os.path.join(root, filename))

    return dir_matches, file_matches

class Searcher(object):

    GREP_TEMPLATE = 'grep ./ -Irne "%s"%s%s'
    INCLUDES_TEMPLATE = ' --include="%s"'
    EXCLUDES_TEMPLATE = ' --exclude-dir="%s" --exclude="%s"'

    def __init__(self, config, file_patterns=[]):
        self.file_patterns = file_patterns
        self.config = config
        self.debug = config.debug

    def _get_exclds(self):
        """Decide which file should be used to build list of paths to ignore."""
        if not self.config.no_ignore:
            return self.config.ignore_file

    def grep_for(self, exp):
        """
        Execute a grep command to search for the given expression.
        Then add each result to self.tree.
        """
        exclds = self._get_exclds()
        cmd = self._grep_cmd(exp, self.file_patterns, exclds)

        results = []
        try:
            response = subprocess.check_output(
                    [cmd],
                    shell=True
                    )
            results = response.splitlines()

            if self.debug:
                print "=== Grep results ==="
                print response, "Total results: %d\n" % len(results)
        except subprocess.CalledProcessError, e:
            if e.returncode == 1:
                print "Couldn't find anything matching '%s'" % exp
            else:
                print "Whoops, grep returned errorcode %d" % e.errorcode
            sys.exit()

        return results

    def _grep_cmd(self, exp, file_patterns, exclude_from=None):
        """Build the grep command used to perform search."""
        excld_flags = ''
        if exclude_from:
            exclds = set()
            excld_dirs = set()
            try:
                with open(exclude_from, 'r') as inp:
                    for row in inp:
                        dirs, files = glob_recursive(row.strip())
                        excld_dirs.update(dirs)
                        exclds.update(files)

            except IOError:
                excld_flags = ''
            else:
                excld_dirs = '" --exclude-dir="'.join(excld_dirs)
                exclds = '" --exclude="'.join(exclds)
                excld_flags = self.EXCLUDES_TEMPLATE % (excld_dirs, exclds)
            finally:
                inclds = ' '.join([self.INCLUDES_TEMPLATE % z for z in file_patterns])
                return self.GREP_TEMPLATE % (exp, excld_flags, inclds)
