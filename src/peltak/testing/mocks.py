""" A place to store all mocks specific to peltak.

Easier to track them down, when you need one.
"""
from typing import Optional

from peltak.core.shell import ExecResult


def mock_result(
    stdout: Optional[str] = None,
    retcode: Optional[int] = None,
    stderr: Optional[str] = None,
    cmd: Optional[str] = None
) -> ExecResult:
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
