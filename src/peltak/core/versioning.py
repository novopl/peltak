# -*- coding: utf-8 -*-
"""
Functionality related to versioning. This makes project version management
much easier.
"""
from __future__ import absolute_import

# stdlib imports
import json
import os
import re
from os.path import exists

from . import conf


RE_PY_VERSION = re.compile(
    r'__version__\s*=\s*["\']'
    r'(?P<version>\d+(\.\d+(\.\d+)?)?)'
    r'["\']'
)
VERSION_FILE = conf.get_path('VERSION_FILE', 'VERSION')


# MAJOR.MINOR[.PATCH[-BUILD]]
RE_VERSION = re.compile(
    r'^'
    r'(?P<major>\d+)'
    r'(\.(?P<minor>\d+)'
    r'(\.(?P<patch>\d+))?)?'
    r'$'
)


def is_valid(version_str):
    """ Check if the given string is a version string

    :param str|unicode version_str:
        A string to check
    :return bool:
        **True** if the given string is a version.
    """
    return version_str and RE_VERSION.match(version_str)


def current():
    """ Return the current project version read from *version_file*.

    :param {str|unicode} version_file:
        Path to the file storing the current version. If not given, it will
        look for file called VERSION in the project root directory.
    :return str|unicode:
        The current project version in MAJOR.MINOR.PATCH format. PATCH might be
        omitted if it's 0, so 1.0.0 becomes 1.0 and 0.1.0 becomes 0.1.
    """
    storage = get_version_storage(VERSION_FILE)
    return storage.read()


def write(version):
    """ Write the given version to the VERSION_FILE """
    storage = get_version_storage(VERSION_FILE)
    storage.write(version)


def bump(component='patch', exact=None):
    """ Bump the given version component.

    :param str version:
        The current version. The format is: MAJOR.MINOR[.PATCH].
    :param str component:
        What part of the version should be bumped. Can be one of:

        - major
        - minor
        - patch

    :return str:
        Bumped version as a string.
    """
    old_ver = current()

    if is_valid(exact):
        new_ver = exact
    else:
        new_ver = _bump_version(old_ver, component)

    write(new_ver)
    return old_ver, new_ver


def _bump_version(version, component='patch'):
    """ Bump the given version component.

    :param str version:
        The current version. The format is: MAJOR.MINOR[.PATCH].
    :param str component:
        What part of the version should be bumped. Can be one of:

        - major
        - minor
        - patch

    :return str:
        Bumped version as a string.
    """
    if component not in ('major', 'minor', 'patch'):
        raise ValueError("Invalid version component: {}".format(component))

    m = RE_VERSION.match(version)
    if m is None:
        raise ValueError("Version must be in MAJOR.MINOR[.PATCH] format")

    major = m.group('major')
    minor = m.group('minor') or '0'
    patch = m.group('patch') or None

    if patch == '0':
        patch = None

    if component == 'major':
        major = str(int(major) + 1)
        minor = '0'
        patch = None

    elif component == 'minor':
        minor = str(int(minor) + 1)
        patch = None

    else:
        patch = patch or 0
        patch = str(int(patch) + 1)

    new_ver = '{}.{}'.format(major, minor)
    if patch is not None:
        new_ver += '.' + patch

    return new_ver


class VersionStorage(object):
    def __init__(self, version_file):
        self.version_file = version_file

        if not exists(version_file):
            raise ValueError("Version file '{}' does not exist.".format(
                version_file
            ))

    def read(self):
        raise NotImplemented("{} must implement .read()".format(
            self.__class__.__name__
        ))

    def write(self, version):
        raise NotImplemented("{} must implement .write()".format(
            self.__class__.__name__
        ))


class PyVersionStorage(VersionStorage):
    def read(self):
        with open(self.version_file) as fp:
            content = fp.read()
            m = RE_PY_VERSION.search(content)
            if not m:
                print("Not found")
            else:
                return m.group('version')

    def write(self, version):
        with open(self.version_file) as fp:
            content = fp.read()

        ver_statement = "__version__ = '{}'".format(version)
        new_content = RE_PY_VERSION.sub(ver_statement, content)

        with open(self.version_file, 'w') as fp:
            fp.write(new_content)


class RawVersionStorage(VersionStorage):
    def read(self):
        with open(self.version_file) as fp:
            return fp.read().strip()

    def write(self, version):
        with open(self.version_file, 'w') as fp:
            fp.write(version)


class NodeVersionStorage(VersionStorage):
    def read(self):
        with open(self.version_file) as fp:
            config = json.load(fp)
            return config.get('version')

    def write(self, version):
        with open(self.version_file, 'rw') as fp:
            config = json.load(fp)

            config['version'] = version

            fp.seek(0, os.SEEK_SET)
            fp.write(version)


def get_version_storage(version_file):
    if VERSION_FILE.endswith('.py'):
        return PyVersionStorage(version_file)
    elif VERSION_FILE.endswith('package.json'):
        return NodeVersionStorage(version_file)
    else:
        return RawVersionStorage(version_file)
