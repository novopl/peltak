# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
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
""" Lint command implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from collections import OrderedDict
from itertools import chain
from types import FunctionType
from typing import List

# 3rd party imports
from six import string_types

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import fs
from peltak.core import git
from peltak.core import log
from peltak.core import shell
from peltak.core import util


g_tools = OrderedDict()


def lint(exclude, skip_untracked, commit_only):
    # type: (List[str], bool, bool) -> None
    """ Lint python files.

    Args:
        exclude (list[str]):
            A list of glob string patterns to test against. If the file/path
            matches any of those patters, it will be filtered out.
        skip_untracked (bool):
            If set to **True** it will skip all files not tracked by git.
        commit_only (bool):
            Only lint files that are staged for commit.
    """
    exclude = list(exclude) + conf.get('lint.exclude', [])
    runner = LintRunner(exclude, skip_untracked, commit_only)

    if not runner.run():
        exit(1)


def tool(name):
    # type: (str) -> FunctionType
    """ Decorator for defining lint tools.

    Args:
        name (str):
            The name of the tool. This name will be used to identify the tool
            in `pelconf.yaml`.
    """
    global g_tools

    def decorator(fn):  # pylint: disable=missing-docstring
        # type: (FunctionType) -> FunctionType
        g_tools[name] = fn
        return fn

    return decorator


class LintRunner(object):
    """ Lint runner class.

    This class represents a single linter run that includes running all the
    tools configured. It will notify the user about progress through stdout.
    """
    def __init__(self, exclude, skip_untracked, commit_only):
        # type: (List[str], bool, bool) -> None
        """ Run static analysis on the given files.

        Args:
            exclude (list[str]):
                A list of glob string patterns to test against. If the file/path
                matches any of those patters, it will be filtered out.
            skip_untracked (bool):
                If set to **True** it will skip all files not tracked by git.
            commit_only (bool):
                Only lint files that are staged for commit.
            linters (list[Tool]):
                A list of linters to run against the code.

        Returns:
            bool: **True** if linting did not return any errors, **False**
            otherwise.
        """
        self.exclude = exclude
        self.skip_untracked = skip_untracked
        self.commit_only = commit_only
        self.allow_empty = True
        self.verbose = context.get('verbose', 0)

        self.linters = OrderedDict()
        for tool in conf.get('lint.tools', ['pep8', 'pylint']):
            if tool in g_tools:
                self.linters[tool] = g_tools[tool]
            else:
                log.err("Unknown lint tool <35>{}", tool)

    def run(self):
        # type: () -> bool
        """ Run all linters and report results.

        Returns:
            bool: **True** if all checks were successful, **False** otherwise.
        """
        with util.timed_block() as t:
            files = self._collect_files()

        log.info("Collected <33>{} <32>files in <33>{}s".format(
            len(files), t.elapsed_s
        ))
        if self.verbose:
            for p in files:
                log.info("  <0>{}", p)

        # No files to lint - return success if empty runs are allowed.
        if not files:
            return self.allow_empty

        with util.timed_block() as t:
            results = self._run_checks(files)

        log.info("Code checked in <33>{}s", t.elapsed_s)

        success = True
        for name, retcodes in results.items():
            if any(x != 0 for x in retcodes):
                success = False
                log.err("<35>{} <31>failed with: <33>{}".format(
                    name, retcodes
                ))

        return success

    def _run_checks(self, files):
        # type: (List[str]) -> OrderedDict[str, int]
        batch_size = conf.get('lint.batch_size', 500)
        results = OrderedDict()

        for name, check_fn in self.linters.items():
            log.info("Running <35>{}".format(name))

            for i, batch in enumerate(util.in_batches(files, batch_size)):
                if len(files) > batch_size:
                    log.info("<0><1>Batch {}<0> <33>[{} files]".format(
                        i + 1, len(batch)
                    ))
                    if self.verbose:
                        for i, path in enumerate(batch):
                            log.info(" {:3}) <0>{}", i + 1, path)

                retcode = check_fn(batch)
                batch_results = results.setdefault(name, [])
                batch_results.append(retcode)
                # if name not in results or retcode != 0:
                #     results[name] = retcode

        return results

    def _collect_files(self):
        # type: () -> List[str]
        paths = [conf.proj_path(p) for p in conf.get('lint.paths', [])]
        exclude = list(self.exclude)
        exclude = exclude or conf.get('lint.exclude', [])

        # prepare
        if self.commit_only:
            include = ['*' + f for f in git.staged() if f.endswith('.py')]
            exclude += git.ignore()
        else:
            include = ['*.py']

        if self.skip_untracked:
            exclude += git.untracked()

        if isinstance(paths, string_types):
            raise ValueError("paths must be an array of strings")

        log.info("Paths to lint:")
        for path in paths:
            log.info("  <0>{}", path)

        return list(chain.from_iterable(
            fs.filtered_walk(p, include, exclude) for p in paths
        ))


@tool('pep8')
def pep8_check(files):
    # type: (List[str]) -> int
    """ Run code checks using pep8.

    Args:
        files (list[str]):
            A list of files to check

    Returns:
        bool: **True** if all files passed the checks, **False** otherwise.

    pep8 tool is **very** fast. Especially compared to pylint and the bigger the
    code base the bigger the difference. If you want to reduce check times you
    might disable all pep8 checks in pylint and use pep8 for that. This way you
    use pylint only for the more advanced checks (the number of checks enabled
    in pylint will make a visible difference in it's run times).
    """
    files = fs.wrap_paths(files)
    cfg_path = conf.get_path('lint.pep8_cfg', 'ops/tools/pep8.ini')
    pep8_cmd = 'pep8 --config {} {}'.format(cfg_path, files)

    return shell.run(pep8_cmd, exit_on_error=False).return_code


@tool('pylint')
def pylint_check(files):
    # type: (List[str]) -> int
    """ Run code checks using pylint.

    Args:
        files (list[str]):
            A list of files to check

    Returns:
        bool: **True** if all files passed the checks, **False** otherwise.
    """
    files = fs.wrap_paths(files)
    cfg_path = conf.get_path('lint.pylint_cfg', 'ops/tools/pylint.ini')
    pylint_cmd = 'pylint --rcfile {} {}'.format(cfg_path, files)

    return shell.run(pylint_cmd, exit_on_error=False).return_code


# Used in type hints comments only (until we drop python2 support)
del FunctionType, List
