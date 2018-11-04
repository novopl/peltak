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
""" Helpers for testing peltak related code.

This is kept inside the peltak package as it ca be used by 3rd party packages
extending the app.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import shutil
import tempfile
from contextlib import contextmanager
from functools import wraps
from os.path import basename, join
from types import FunctionType
from typing import Any, Dict, List, Union

# 3rd party imports
from mock import patch, Mock
from peltak.core.shell import ExecResult


class patch_proj_root(object):
    """ Patch project root decorator. """
    def __init__(self, proj_root, nest_level=0):
        self.proj_root = proj_root
        self.nest = nest_level

    def __call__(self, fn):
        if self.proj_root is not None:
            cwd = join(self.proj_root, *(['fake_dir'] * self.nest))
            dirs = ['not_pelconf'] * self.nest + ['pelconf.py']
            dirs = [[d] for d in dirs]
        else:
            cwd = join('/', *(['fake_dir'] * self.nest))
            dirs = [[d] for d in ['not_pelconf'] * self.nest]

        @patch('os.getcwd', Mock(return_value=cwd))
        @patch('os.listdir', Mock(side_effect=dirs))
        @wraps(fn)
        def wrapper(*args, **kw):       # pylint: disable=missing-docstring
            return fn(*args, **kw)

        return wrapper


def patch_pelconf(config):
    # type: (Dict[str, Any]) -> FunctionType
    """ Patch the peltak configuration.

    This will patch all content retrieved through `peltak.core.conf.get()` and
    `conf.get_path()`.

    Args:
        config (dict[str, Any]):
            The dictionary with the peltak configuration.
    """
    return patch('peltak.core.conf.g_config', config)


def mock_response(data):
    # type: (Union[Dict[str, Any], List[Any]]) -> Mock
    """ Create a mock response that can be set as requests return value.

    Args:
        data (Union[dict[str, Any], list[Any]]):

    Returns:
        MagicMock:
    """
    resp_mock = Mock()
    resp_mock.json = Mock(return_value=data)
    return resp_mock


class TestDataProvider(object):
    """ Provides a temporary copy of the selected test project. """

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.proj_dir = None

    @contextmanager
    def __call__(self, path):
        temp_dir = tempfile.mkdtemp(prefix='peltak_tests_')

        cwd = os.getcwd()
        self.proj_dir = join(temp_dir, basename(path))
        proj_src = join(self.data_dir, path)

        shutil.copytree(proj_src,  self.proj_dir)
        os.chdir(self.proj_dir)

        try:
            yield self
        finally:
            os.chdir(cwd)
            shutil.rmtree(temp_dir)


def mock_result(stdout=None, retcode=None, stderr=None, cmd=None):
    # type: (str, int, str, str) -> ExecResult
    """ Helper for creating ExecResults for tests.

    Args:
        stdout (str):
        retcode (int):
        stderr (str):
        cmd (str):

    Returns:
        ExecResult:
    """
    return ExecResult(
        cmd or '',
        retcode or 0,
        stdout or '',
        stderr or '',
        retcode == 0,
        retcode != 0,
    )


def patch_run(stdout=None, retcode=None, stderr=None, cmd=None):
    # type: (str, int, str, str) -> FunctionType
    """ Patch shell.run and make it return a given result.

    Args:
        stdout (str):
        retcode (int):
        stderr (str):
        cmd (str):

    Returns:
        FunctionType:

    """
    p_run = Mock(return_value=ExecResult(
        cmd or '',
        retcode or 0,
        stdout or '',
        stderr or '',
        retcode == 0,
        retcode != 0,
    ))

    return patch('peltak.core.shell.run', p_run)
