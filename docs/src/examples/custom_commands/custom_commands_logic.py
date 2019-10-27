# -*- coding: utf-8 -*-
""" Custom commands business logic. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Sequence

# local imports
from peltak.core import fs
from peltak.core import log
from peltak.core import shell
from peltak.core import types


def check(paths, include, exclude, only_staged, untracked):
    # type: (str, Sequence[str], Sequence[str], bool, bool) -> None
    """ Run mypy and pylint against the current directory."""

    files = types.FilesCollection(
        paths=paths,
        include=['*.py'] + list(include),     # We only want to lint python files.
        exclude=exclude,
        only_staged=only_staged,
        untracked=untracked,
    )

    paths = fs.collect_files(files)
    wrapped_paths = fs.wrap_paths(paths)

    log.info("Paths:            <33>{}", paths)
    log.info("Wrapped paths:    <33>{}", wrapped_paths)

    log.info("Running <35>mypy")
    shell.run('mypy --ignore-missing-imports {}'.format(wrapped_paths))

    log.info("Running <35>pylint")
    shell.run('pylint {}'.format(wrapped_paths))


# Used only in type hint comments
del Sequence
