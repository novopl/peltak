# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch, mock_open

# local imports
from peltak.core import git


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
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))


@patch('peltak.core.git.open', mock_open(read_data='\n'.join([
    'pattern1',
    ' pattern2   \t',
    '\tpattern3',
])))
def test_strips_whitespace():
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))


@patch('peltak.core.git.open', mock_open(read_data='\n'.join([
    'pattern1',
    ''
    ' pattern2   \t',
    ''
    '\tpattern3',
    ''
])))
def test_skips_empty_lines():
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))


@patch('peltak.core.git.open', mock_open(read_data=b'\n'.join([
    b'pattern1',
    b''
    b' pattern2   \t',
    b''
    b'\tpattern3',
    b''
])))
def test_works_if_parse_data_is_bytes():
    assert frozenset(git.ignore()) == frozenset((
        'pattern1',
        'pattern2',
        'pattern3'
    ))
