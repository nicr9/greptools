from setuptools import setup
VERSION = '0.9a'

try:
    import subprocess
    subprocess.call(["pandoc", "--from=markdown", "--to=rst", "README.md", "-o", "README.rst"])
except:
    pass

setup(
        name='greptools',
        version=VERSION,
        description='A collection of grep wrappers and tools for various filetypes.',
        author='Nic Roland',
        author_email='nicroland9@gmail.com',
        url='https://github.com/nicr9/greptools',
        download_url='https://github.com/nicr9/greptools/tarball/%s' % VERSION,
        packages=['greptools', 'greptools.reader', "greptools.test"],
        scripts=['bin/pygt', 'bin/mdgt', 'bin/javagt'],
        install_requires=['mock'],
        test_suite="greptools.test",
        long_description=open('README.rst').read(),
        )
