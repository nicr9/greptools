import subprocess
import os.path
from sys import exit as sys_exit

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
    """Constructs and executes grep queries."""
    GREP_TEMPLATE = 'grep ./ -Irne "%s"%s%s'
    INCLUDES_TEMPLATE = ' --include="%s"'
    EXCLUDES_TEMPLATE = ' --exclude="%s"'
    EXCLUDE_DIRS_TEMPLATE = ' --exclude-dir="%s"'

    def __init__(self, config, file_patterns=[]):
        self.file_patterns = file_patterns
        self.config = config
        self.debug = config.debug

    def get_exclds(self):
        """Build list of file paths to ignore in upcomming search."""
        if not self.config.no_ignore and self.config.ignore_file:
            exclds = set()
            excld_dirs = set()
            try:
                with open(self.config.ignore_file, 'r') as inp:
                    for row in inp:
                        row = row.strip()
                        if row[0] == '*':
                            dirs, files = glob_recursive(row)
                            excld_dirs.update(dirs)
                            exclds.update(files)
                        elif os.path.isfile(row):
                            exclds.add(os/path.join('./', row))
                        elif os.path.isdir(row):
                            row = row.rstrip('/')
                            if not row[:2] == './':
                                row = os.path.join('./', row)
                            excld_dirs.add(row)
                        else:
                            continue
            except IOError:
                pass

            return exclds, excld_dirs
        else:
            return [], []

    def grep_for(self, exp):
        """
        Execute a grep command to search for the given expression.
        Results are returned as a list.
        """
        cmd = self._grep_cmd(exp, self.file_patterns)

        try:
            response = subprocess.check_output(
                    [cmd],
                    shell=True
                    )
            results = response.splitlines()

            if self.debug:
                print "=== Grep results ==="
                print response, "Total results: %d\n" % len(results)
        except subprocess.CalledProcessError, err:
            if err.returncode == 1:
                print "Couldn't find anything matching '%s'" % exp
            else:
                print "Whoops, grep returned errorcode %d" % err.errorcode
            sys_exit()

        return results

    def _grep_cmd(self, exp, file_patterns):
        """Build the grep command used to perform search."""
        exclds, excld_dirs = self.get_exclds()

        if self.debug:
            print "=== Excluded files ==="
            for exf in exclds:
                print exf
            print
            print "=== Excluded dirs ==="
            for exd in excld_dirs:
                print exd
            print

        # Turn list of excluded files into string of CLI flags
        exclds = ''.join([self.EXCLUDES_TEMPLATE % z for z in exclds])
        excld_dirs = ''.join(
                [self.EXCLUDE_DIRS_TEMPLATE % z for z in excld_dirs]
                )
        excld_flags = exclds + excld_dirs

        # Turn list of included filetypes into string of CLI flags
        inclds = ' '.join([self.INCLUDES_TEMPLATE % z for z in file_patterns])

        return self.GREP_TEMPLATE % (exp, excld_flags, inclds)
