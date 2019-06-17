from distutils.core import setup

from setuptools import find_packages

setup(
        name='sam',
        packages=find_packages(include=['*'], exclude=['tests.*']),
        package_data={
            '': ['*.exe', '*'],
        },
        version='1.0.0',
        install_requires=['Click', 'pyfiglet', 'selenium', 'boto3', 'pygrok'],
        entry_points='''
        [console_scripts]
        sam=sam.entrypoint:cli
        ''',
)
