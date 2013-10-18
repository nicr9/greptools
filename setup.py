from distutils.core import setup

setup(
        name='pygt',
        version='0.5a',
        description='Python Grep Tool',
        author='Nic Roland',
        author_email='nicroland9@gmail.com',
        packages=['pygt'],
        scripts = ['bin/pygt'],
        long_description=open('README.md').read(),
        )
