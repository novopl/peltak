# pylint: disable=missing-docstring
import pytest

from peltak.core import conf


@pytest.mark.parametrize('proj_path,abs_path', [
    ('testfile', '/fake/proj/testfile'),
    ('sub/testfile', '/fake/proj/sub/testfile'),
    ('/abs/path', '/abs/path'),
])
def test_converts_project_path_to_an_absolute_path(proj_path, abs_path):
    # Patch project root location
    app_conf = conf.Config({}, path='/fake/proj/pelconf.yaml')

    assert app_conf.proj_path(proj_path) == abs_path


def test_returns_input_path_if_no_project_root_found():
    # setattr(pelconf._find_proj_root, util.cached_result.CACHE_VAR, None)
    app_conf = conf.Config()

    assert app_conf.proj_path('hello/world') == 'hello/world'


def test_can_join_paths():
    app_conf = conf.Config(path='/fake/proj/pelconf.yaml')

    assert app_conf.proj_path('sub', 'testfile') == '/fake/proj/sub/testfile'


def test_works_with_abspath_split_into_parts():
    app_conf = conf.Config(path='/fake/proj/pelconf.yaml')

    assert app_conf.proj_path('/sub', 'testfile') == '/sub/testfile'
