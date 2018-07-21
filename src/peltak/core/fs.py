# -*- coding: utf-8 -*-
"""
File system related helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from os.path import exists, isdir
from shutil import rmtree

# 3rd party imports
from six import string_types

# local imports
from . import log
from . import shell


def surround_paths_with_quotes(paths):
    """ Put quotes around all paths and join them with space in between. """
    if isinstance(paths, string_types):
        raise ValueError(
            "paths cannot be a string. "
            "Use array with one element instead."
        )
    return ' '.join('"' + path + '"' for path in paths)


def rm_glob(pattern, exclude_env=True, exclude_tox=True):
    """ Remove all files matching the given glob *pattern*. """
    log.info("Removing files matching {}", pattern)

    cmd = ['find . -name "{}"'.format(pattern)]

    if exclude_env:
        # Remove entries starting with ./env
        cmd.append("| sed '/^\.\/env/d'")

    if exclude_tox:
        # Remove entries starting with ./.tox
        cmd.append("| sed '/^\.\/\.tox/d'")

    matches = shell.run(' '.join(cmd), capture=True)

    for path in matches.stdout.splitlines():
        # might be a child of a dir deleted in an earlier iteration
        if not exists(path):
            continue

        try:
            if not isdir(path):
                log.info('  <91>[file] <90>{}', path)
                os.remove(path)
            else:
                log.info('  <91>[dir]  <90>{}', path)
                rmtree(path)
        except OSError:
            log.info("<33>Failed to remove <90>{}", path)
