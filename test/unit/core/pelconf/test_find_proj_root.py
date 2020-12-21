# pylint: disable=missing-docstring
from os.path import join
from functools import wraps
from unittest.mock import Mock, patch

from peltak.core import pelconf
from peltak.core import util


class patch_pelconf_location(object):
    """ Patch project root decorator. """
    def __init__(self, proj_root, nest_level=0):
        self.proj_root = proj_root
        self.nest = nest_level

    def __call__(self, fn):
        if self.proj_root is not None:
            cwd = join(self.proj_root, *(['fake_dir'] * self.nest))
            dirs = ['not_pelconf'] * self.nest + [pelconf.DEFAULT_PELCONF_NAME]
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


@patch_pelconf_location('/fake/proj/root')
def test_runs_detection_when_no_global_variable_stored():
    util.cached_result.clear(pelconf._find_proj_root)
    assert pelconf._find_proj_root() == '/fake/proj/root'

    util.cached_result.clear(pelconf._find_proj_root)


@patch_pelconf_location('/fake/proj/root', nest_level=2)
def test_works_with_multiple_levels_of_nesting():
    util.cached_result.clear(pelconf._find_proj_root)
    assert pelconf._find_proj_root() == '/fake/proj/root'

    util.cached_result.clear(pelconf._find_proj_root)


@patch_pelconf_location(None)
def test_returns_none_if_not_found():
    util.cached_result.clear(pelconf._find_proj_root)
    assert pelconf._find_proj_root() is None

    util.cached_result.clear(pelconf._find_proj_root)
