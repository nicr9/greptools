from distutils.core import setup

setup(
        name='greptools',
        version='v0.7',
        description='A collection of grep wrappers for various filetypes.',
        author='Nic Roland',
        author_email='nicroland9@gmail.com',
        packages=['greptools', 'greptools.reader'],
        scripts = ['bin/pygt', 'bin/mdgt', 'bin/javagt'],
        long_description=open('README.md').read(),
        )
