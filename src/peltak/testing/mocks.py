# -*- coding: utf-8 -*-
""" A place to store all mocks specific to peltak.

Easier to track them down, when you need one.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any, Dict, List, Union

# 3rd party imports
from mock import Mock

# local imports
from peltak.core.shell import ExecResult


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


# Used only in type hint comments
del Any, Dict, List, Union
