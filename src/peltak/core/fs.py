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
.. module:: peltak.core.fs
    :synopsis: File system related helpers.
"""
import fnmatch
import itertools
import os
import re
from os.path import isdir, join, normpath
from typing import Iterator, List, Optional, Union

from . import conf, context, log, types


def wrap_paths(paths: List[str]) -> str:
    """ Put quotes around all paths and join them with space in-between. """
    if isinstance(paths, str):
        raise ValueError(
            "paths cannot be a string. "
            "Use array with one element instead."
        )
    return ' '.join('"' + path + '"' for path in paths)


def filtered_walk(
    path: str,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None
) -> Iterator[str]:
    """ Walk recursively starting at *path* excluding files matching *exclude*

    Args:
        path:
            A starting path. This has to be an existing directory.
        include:
            A white list of glob patterns. If given, only files that match those
            globs will be yielded (filtered by exclude).
        exclude:
            A list of glob string patterns to test against. If the file/path
            matches any of those patters, it will be filtered out.

    Returns:
        A generator yielding all the files that do not match any
        pattern in ``exclude``.
    """
    exclude = exclude or []

    if not isdir(path):
        raise ValueError("Cannot walk files, only directories: {}".format(path))

    files = os.listdir(path)
    for name in files:
        filename = normpath(join(path, name))

        # If excluded, completely skip it. Will not recurse into directories
        if search_globs(filename, exclude):
            continue

        # If we have a whitelist and the pattern matches, yield it. If the
        # pattern didn't match and it's a dir, it will still be recursively
        # processed.
        if not include or match_globs(filename, include):
            yield filename

        if isdir(filename):
            for p in filtered_walk(filename, include, exclude):
                yield p


def match_globs(path: str, patterns: List[str]) -> bool:
    """ Test whether the given *path* matches any patterns in *patterns*

    Args:
        path (str):
            A file path to test for matches.
        patterns (list[str]):
            A list of glob string patterns to test against. If *path* matches
            any of those patters, it will return True.

    Returns:
        bool: **True** if the *path* matches any pattern in *patterns*.
    """
    for pattern in (p for p in patterns if p):
        if pattern.startswith('/'):
            regex = fnmatch.translate(pattern[1:])

            temp_path = path[1:] if path.startswith('/') else path

            m = re.search(regex, temp_path)

            if m and m.start() == 0:
                return True

        elif fnmatch.fnmatch(path, pattern):
            return True

    return False


def search_globs(path: str, patterns: List[str]) -> bool:
    """ Test whether the given *path* contains any patterns in *patterns*

    Args:
        path (str):
            A file path to test for matches.
        patterns (list[str]):
            A list of glob string patterns to test against. If *path* matches
            any of those patters, it will return True.

    Returns:
        bool: **True** if the ``path`` matches any pattern in *patterns*.
    """
    for pattern in (p for p in patterns if p):
        if pattern.startswith('/'):
            # If pattern starts with root it means it match from root only
            regex = fnmatch.translate(pattern[1:])
            regex = regex.replace('\\Z', '')

            temp_path = path[1:] if path.startswith('/') else path
            m = re.search(regex, temp_path)

            if m and m.start() == 0:
                return True

        else:
            regex = fnmatch.translate(pattern)
            regex = regex.replace('\\Z', '')

            if re.search(regex, path):
                return True

    return False


def write_file(path: str, content: Union[str, bytes], mode: str = 'w') -> None:
    """ --pretend aware file writing.

    You can always write files manually but you should always handle the
    --pretend case.

    Args:
        path (str):
        content (str):
        mode (str):
    """
    from peltak.core import context, log

    if context.get('pretend', False):
        log.info("Would overwrite <34>{path}<32> with:\n<90>{content}",
                 path=path,
                 content=content)
    else:
        with open(path, mode) as fp:
            fp.write(content)


def collect_files(files: types.FilesCollection) -> List[str]:
    """ Collect files using the given configuration. """
    paths = [conf.proj_path(p) for p in files.paths]

    if context.RunContext().get('verbose', 0) >= 3:
        log.info("<35>Files:")
        log.info("only_staged: <33>{}".format(files.only_staged))
        log.info("untracked: <33>{}".format(files.untracked))
        log.info("whitelist: <33>\n{}".format('\n'.join(files.whitelist())))
        log.info("blacklist: <33>\n{}".format('\n'.join(files.blacklist())))

    if files.only_staged and files.include and not files.whitelist():
        # include will be empty if none of the staged files match include
        # and thus the final fs walk will pick up everything. We want
        # to preserve the include patterns defined in `pelconf.yaml`
        # so nothing is picked if none of the staged files match.
        return []

    return list(itertools.chain.from_iterable(
        filtered_walk(path, files.whitelist(), files.blacklist())
        for path in paths
    ))
