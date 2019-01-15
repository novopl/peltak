import os
import re
import sys
from setuptools import setup, find_packages


RE_PY_VERSION = re.compile(
    r'__version__\s*=\s*["\']'
    r'(?P<version>\d+(\.\d+(\.\d+)?)?)'
    r'["\']'
)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_version():
    content = read('src/peltak/__init__.py')
    m = RE_PY_VERSION.search(content)
    if not m:
        return '0.0'
    else:
        return m.group('version')


requirements = [
    'click~=7.0',
    'PyYAML~=3.0',
    'six~=1.11',
    'attrs~=18.2',
]
if sys.version_info < (3, 5):
    requirements += ['typing~=3.6']


setup(
    name="peltak",
    version=read_version(),
    author="Mateusz 'novo' Klos",
    author_email="novopl@gmail.com",
    license="Apache 2.0",
    keywords="fabric ops devops",
    url="http://github.com/novopl/peltak",
    description="Set of CLI commands to help manage a project",
    long_description=read('README.rst'),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'peltak = peltak.main:root_cli',
        ]
    },
    package_data={
        'peltak': [
            'templates/*'
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
