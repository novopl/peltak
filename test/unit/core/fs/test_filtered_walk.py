# pylint: disable=missing-docstring
import pytest

from peltak.core import fs


@pytest.fixture
def test_project(unit_test_data):
    with unit_test_data('filtered_walk') as loader:
        yield loader


def test_shows_all_files(test_project):
    result = frozenset(fs.filtered_walk('.'))

    assert result == frozenset((
        'ops',
        'ops/tools',
        'ops/tools/pylint.ini',
        'ops/tools/pytest.ini',
        'src',
        'src/pkg',
        'src/pkg/__init__.py',
        'pelconf.yaml',
        'README.rst',
    ))


def test_raises_ValueError_if_path_is_not_a_directory(test_project):
    with pytest.raises(ValueError):
        list(fs.filtered_walk('pelconf.py'))


def test_exclude_works(test_project):
    result = frozenset(fs.filtered_walk('.', exclude=['*ops*']))
    assert result == frozenset((
        'src',
        'src/pkg',
        'src/pkg/__init__.py',
        'pelconf.yaml',
        'README.rst',
    ))


def test_exclude_abspath_means_relative_to_starting_point(test_project):
    result = frozenset(fs.filtered_walk('.', exclude=['/ops*']))
    assert result == frozenset((
        'src',
        'src/pkg',
        'src/pkg/__init__.py',
        'pelconf.yaml',
        'README.rst',
    ))


def test_include_works(test_project):
    result = frozenset(fs.filtered_walk('.', include=['ops*']))
    assert result == frozenset((
        'ops',
        'ops/tools',
        'ops/tools/pylint.ini',
        'ops/tools/pytest.ini',
    ))


def test_include_abspath_means_relative_to_starting_point(test_project):
    result = frozenset(fs.filtered_walk('.', include=['/ops*']))
    assert result == frozenset((
        'ops',
        'ops/tools',
        'ops/tools/pylint.ini',
        'ops/tools/pytest.ini',
    ))
