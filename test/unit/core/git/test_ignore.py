# pylint: disable=missing-docstring
from unittest.mock import patch, mock_open

from peltak.core import git
from peltak.core import util


FAKE_GIT_IGNORE = '\n'.join([
    'pattern1',
    'pattern2',
    '/pattern3',
])


@patch('peltak.core.git.open', mock_open(read_data='\n'.join([
    'pattern1',
    'pattern2',
    'pattern3',
])))
def test_returns_all_patterns():
    util.cached_result.clear(git.ignore)
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))
    util.cached_result.clear(git.ignore)


@patch('peltak.core.git.open', mock_open(read_data='\n'.join([
    'pattern1',
    ' pattern2   \t',
    '\tpattern3',
])))
def test_strips_whitespace():
    util.cached_result.clear(git.ignore)
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))
    util.cached_result.clear(git.ignore)


@patch('peltak.core.git.open', mock_open(read_data='\n'.join([
    'pattern1',
    ''
    ' pattern2   \t',
    ''
    '\tpattern3',
    ''
])))
def test_skips_empty_lines():
    util.cached_result.clear(git.ignore)
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))
    util.cached_result.clear(git.ignore)


@patch('peltak.core.git.open', mock_open(read_data=b'\n'.join([
    b'pattern1',
    b''
    b' pattern2   \t',
    b''
    b'\tpattern3',
    b''
])))
def test_works_if_parse_data_is_bytes():
    util.cached_result.clear(git.ignore)
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))
    util.cached_result.clear(git.ignore)
