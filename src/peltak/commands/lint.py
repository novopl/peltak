# -*- coding: utf-8 -*-
""" Code linting commands. """
from __future__ import absolute_import
from . import cli, click


def _lint_files(paths, excluded=None):
    """ Run static analysis on the given files.

    :param paths:   Iterable with each item being path that should be linted..
    """
    from itertools import chain
    from six import string_types
    from peltak.core import conf
    from peltak.core import fs
    from peltak.core import log
    from peltak.core import shell

    pylint_cfg_path = conf.get_path('PYLINT_CFG_PATH', 'ops/tools/pylint.ini')
    pep8_cfg_path = conf.get_path('PEP8_CFG_PATH', 'ops/tools/pep8.ini')

    if isinstance(paths, string_types):
        raise ValueError("paths must be an array of strings")

    log.info("Linting")
    for path in paths:
        print("--   {}".format(path))

    files = fs.surround_paths_with_quotes(chain.from_iterable(
        fs.filtered_walk(p, include=["*.py"], exclude=excluded) for p in paths
    ))

    log.info("Checking PEP8 compatibility")
    pep8_cmd = 'pep8 --config {} {{}}'.format(pep8_cfg_path)
    pep8_ret = shell.run(pep8_cmd.format(files)).return_code

    log.info("Running linter")
    pylint_cmd = 'pylint --rcfile {} {{}}'.format(pylint_cfg_path)
    pylint_ret = shell.run(pylint_cmd.format(files)).return_code

    if pep8_ret != 0:
        print("pep8 failed with return code {}".format(pep8_ret))

    if pylint_ret:
        print("pylint failed with return code {}".format(pylint_ret))

    return pep8_ret == pylint_ret == 0


@cli.command()
@click.option(
    '--ignore',
    type=str,
    help='Comma separated list of paths to ignore'
)
def lint(ignore):
    """ Run pep8 and pylint on all project files.

    You can configure the linting paths using the LINT_PATHS config variable.
    This should be a list of paths that will be linted. If a path to a directory
    is given, all files in that directory and it's subdirectories will be
    used.

    The pep8 and pylint config paths are by default stored in ops/tools/pep8.ini
    and ops/tools/pylint.ini. You can customise those paths in your config with
    PEP8_CFG_PATH and PYLINT_CFG_PATH variables.
    """
    import time
    from itertools import chain
    from peltak.core import conf
    from peltak.core import fs
    from peltak.core import log

    ignore = ignore or []

    if ignore:
        ignore = ignore.split(',')

    paths = [conf.proj_path(p) for p in conf.get('LINT_PATHS', [])]

    t0 = time.time()
    files = list(chain.from_iterable(
        fs.filtered_walk(p, include=["*.py"], exclude=ignore) for p in paths
    ))
    elapsed_ms = round((time.time() - t0) * 1000, 3)

    for p in files:
        log.info("  - <34>{}".format(p))

    log.info("Collected {} files in {}ms".format(len(files), elapsed_ms))

    if not _lint_files(paths, ignore):
        exit(1)
