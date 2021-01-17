# Copyright 2017-2020 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import re
from collections import OrderedDict
from os.path import exists
from typing import Optional

from peltak.core import fs, util


RE_PY_VERSION = re.compile(
    r'__version__\s*=\s*["\']'
    r'(?P<version>\d+(\.\d+(\.\d+)?)?)'
    r'["\']'
)
# major.minor[.patch[-build]]
RE_VERSION = re.compile(
    r'^'
    r'(?P<major>\d+)'
    r'(\.(?P<minor>\d+)'
    r'(\.(?P<patch>\d+))?)?'
    r'$'
)


class InvalidVersionFile(RuntimeError):
    pass


def is_valid(version_str: str) -> bool:
    """ Check if the given string is a version string

    Args:
        version_str (str):
            A string to check

    Returns:
        bool: **True** if the given string is a version.
    """
    return bool(version_str and RE_VERSION.match(version_str))


class VersionFile(object):
    """ Base class for version storage.

    A version storage is a way to store the project version. Different projects
    will have different ways of storing the version. The simplest case is a
    text file that holds just the version number (probably called VERSION).
    Python projects can also use a version stored as ``__version__`` variable
    inside the project package/module. A Node.js project on the other hand will
    probably keep the version in ``package.json``. All of the above strategies
    can be (and are) implemented through subclassing this class.

    @see `PyVersionFile`, `RawVersionFile`, `NodeVersionFile`
    """
    def __init__(self, path: str) -> None:
        self.path = path
        if not exists(path):
            raise ValueError(f"Version file '{path}' does not exist.")

    def read(self) -> Optional[str]:
        """ Read the current project version.

        All subclasses must implement this method.

        Raises:
            NotImplementedError:
                If the subclass does nto implement the read() method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement .read()")

    def write(self, version: str):
        """ Save the given version as the current project version.

        All subclasses must implement this method.

        Raises:
            NotImplementedError:
                If the subclass does nto implement the write() method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement .write()")


class PyVersionFile(VersionFile):
    """ Store project version in one of the py module/package files. """
    def read(self) -> Optional[str]:
        """ Read the project version from .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and read the version string.
        """
        with open(self.path) as fp:
            content = fp.read()
            m = RE_PY_VERSION.search(content)
            if not m:
                return None
            else:
                return m.group('version')

    def write(self, version: str):
        """ Write the project version to .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and substitute the version string
        for the new version.
        """
        with open(self.path) as fp:
            content = fp.read()

        ver_statement = "__version__ = '{}'".format(version)
        new_content = RE_PY_VERSION.sub(ver_statement, content)
        fs.write_file(self.path, new_content)


class RawVersionFile(VersionFile):
    """ Store project version as a simple value in a text file. """
    def read(self) -> Optional[str]:
        """ Read the project version from .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and read the version string.
        """
        with open(self.path) as fp:
            version = fp.read().strip()

            if is_valid(version):
                return version

            return None

    def write(self, version: str):
        fs.write_file(self.path, version)


class NodeVersionFile(VersionFile):
    """ Store project version in package.json. """
    def read(self) -> Optional[str]:
        with open(self.path) as fp:
            config = json.load(fp)
            return config.get('version')

    def write(self, version: str):
        with open(self.path, 'r') as fp:
            config = json.load(fp, object_pairs_hook=OrderedDict)

        config['version'] = version

        fs.write_file(self.path, json.dumps(config, indent=2) + '\n')


class PoetryVersionFile(VersionFile):
    """ Store project version in package.json. """
    def read(self) -> Optional[str]:
        config = util.toml_load(self.path)
        return util.get_from_dict(config, 'tool.poetry.version', None)

    def write(self, version: str):
        config = util.toml_load(self.path)
        config['tool']['poetry']['version'] = version

        fs.write_file(self.path, util.toml_dump(config))


# path test -> VersionFile implementation
VERSION_FILE_TYPES = [
    (lambda p: p.endswith('.py'), PyVersionFile),
    (lambda p: p.endswith('package.json'), NodeVersionFile),
    (lambda p: p.endswith('pyproject.toml'), PoetryVersionFile),
    (lambda p: True, RawVersionFile),   # default to Raw version file.
]


def load_version_file(path: str) -> VersionFile:
    for test, cls in VERSION_FILE_TYPES:
        if test(path):
            return cls(path)

    raise InvalidVersionFile()
