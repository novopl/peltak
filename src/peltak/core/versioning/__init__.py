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
"""
.. module:: peltak.core.versioning
    :synopsis: Functionality related to project versioning.
"""
import re
from typing import List, Optional, Tuple

from peltak.core import conf

from .version_file import (  # noqa: F401
    NodeVersionFile,
    PoetryVersionFile,
    PyVersionFile,
    RawVersionFile,
    VersionFile,
    is_valid,
    load_version_file,
)


# MAJOR.MINOR[.PATCH[-BUILD]]
RE_VERSION = re.compile(
    r'^'
    r'(?P<major>\d+)'
    r'(\.(?P<minor>\d+)'
    r'(\.(?P<patch>\d+))?)?'
    r'$'
)


def current() -> str:
    """ Return the project's current version.

    The project is read from the first file on the 'version.files' list. We
    always use the first file on the list as the source of truth, but any
    changes will be written to all files specified on the list.

    Returns:
        str: The current project version in MAJOR.MINOR.PATCH format. PATCH
        might be omitted if it's 0, so 1.0.0 becomes 1.0 and 0.1.0 becomes 0.1.
    """
    version_files = get_version_files()
    if not version_files:
        raise ValueError("No version file configured")

    main_version_file = version_files[0]
    return main_version_file.read() or ''


def write(version: str) -> None:
    """ Write the given version to the VERSION_FILE """
    if not is_valid(version):
        raise ValueError("Invalid version: '{}'".format(version))

    version_files = get_version_files()
    if not version_files:
        raise ValueError("No version file configured")

    for version_file in version_files:
        version_file.write(version)


def bump(component: str = 'patch', exact: Optional[str] = None) -> Tuple[str, str]:
    """ Bump the given version component.

    Args:
        component (str):
            What part of the version should be bumped. Can be one of:

            - major
            - minor
            - patch

        exact (str):
            The exact version that should be set instead of bumping the current
            one.

    Returns:
        tuple(str, str): A tuple of old and bumped version.
    """
    old_ver = current()

    if exact is None:
        new_ver = _bump_version(old_ver, component)
    else:
        new_ver = exact

    write(new_ver)
    return old_ver, new_ver


def _bump_version(version: str, component: str = 'patch') -> str:
    """ Bump the given version component.

    Args:
        version (str):
            The current version. The format is: MAJOR.MINOR[.PATCH].
        component (str):
            What part of the version should be bumped. Can be one of:

            - major
            - minor
            - patch

    Returns:
        str: Bumped version as a string.
    """
    if component not in ('major', 'minor', 'patch'):
        raise ValueError("Invalid version component: {}".format(component))

    m = RE_VERSION.match(version)
    if m is None:
        raise ValueError(
            f"Version must be in MAJOR.MINOR[.PATCH] format, got: '{version}'"
        )

    major = m.group('major')
    minor = m.group('minor') or '0'
    patch = m.group('patch') or None

    if component == 'major':
        major = str(int(major) + 1)
        minor = '0'
        patch = '0'

    elif component == 'minor':
        minor = str(int(minor) + 1)
        patch = '0'

    else:
        patch = patch or '0'
        patch = str(int(patch) + 1)

    new_ver = '{}.{}.{}'.format(major, minor, patch)

    return new_ver


def get_version_files() -> List[VersionFile]:
    version_files = conf.get('version.files', [])

    if not version_files:
        # TODO: 'version.file' is deprecated, use 'version.files' instead.
        single = conf.get('version.file', None)
        version_files = [single] if single else []

    return [load_version_file(conf.proj_path(p)) for p in version_files]
