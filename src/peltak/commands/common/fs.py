# -*- coding: utf-8 -*-
"""
File system related helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os import remove
from os.path import exists, isdir
from shutil import rmtree

# 3rd party imports
from six import string_types
from fabric.api import local, quiet

# local imports
from . import log


def surround_paths_with_quotes(paths):
    """ Put quotes around all paths and join them with space in between. """
    if isinstance(paths, string_types):
        raise ValueError(
            "paths cannot be a string. "
            "Use array with one element instead."
        )
    return ' '.join('"' + path + '"' for path in paths)


def rm_glob(pattern):
    """ Remove all files matching the given glob *pattern*. """
    log.info("Removing files matching {}", pattern)

    with quiet():
        cmd = ' '.join([
            'find . -name "{}"'.format(pattern),
            "| sed '/^\.\/env/d'",   # Remove entries starting with ./env
            "| sed '/^\.\/\.tox/d'"  # Remove entries starting with ./.tox
        ])
        matches = local(cmd, capture=True)

    for path in matches.splitlines():
        # might be a child of a dir deleted in an earlier iteration
        if not exists(path):
            continue

        if not isdir(path):
            log.info('  ^91[file] ^90{}'.format(path))
            remove(path)
        else:
            log.info('  ^91[dir]  ^90{}'.format(path))
            rmtree(path)
