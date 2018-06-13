# -*- coding: utf-8 -*-
"""
Testing commands
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os.path

# 3rd party imports
from fabric.api import local, shell_env

# local imports
from .common import conf
from .common import fs


BUILD_DIR = conf.get_path('BUILD_DIR', '.build')

PYTEST_CFG_PATH = conf.get_path('PYTEST_CFG_PATH', 'ops/tools/pytest.ini')
TEST_TYPES = conf.get('TEST_TYPES', {})

COVERAGE_OUT_PATH = os.path.join(BUILD_DIR, 'coverage')
COVERAGE_CFG_PATH = conf.get_path('COVERAGE_CFG_PATH', 'ops/tools/coverage.ini')

DJANGO_SETTINGS = conf.get('DJANGO_SETTINGS', None)
DJANGO_TEST_SETTINGS = conf.get('DJANGO_TEST_SETTINGS', None)


def test(**opts):
    """ Run all tests against the current python version. """
    SRC_DIR = conf.get_path('SRC_DIR')
    SRC_PATH = conf.get_path('SRC_PATH')

    sugar = conf.is_true(opts.get('sugar', 'on'))
    junit = conf.is_true(opts.get('junit', 'off'))
    test_type = opts.get('type', 'default')
    verbose = int(opts.get('verbose', '0'))
    show_locals = conf.is_true(opts.get('locals', 'on'))
    coverage = conf.is_true(opts.get('coverage', 'on'))
    plugins = opts.get('plugins', '').split(',')

    args = []

    if coverage:
        args += [
            '--durations=3',
            '--cov-config={}'.format(COVERAGE_CFG_PATH),
            '--cov={}'.format(SRC_PATH),
            '--cov-report=term:skip-covered',
            '--cov-report=html:{}'.format(COVERAGE_OUT_PATH),
        ]

    if junit:
        args += ['--junitxml={}/test-results.xml'.format('.build')]

    if '-django' not in plugins:
        if DJANGO_TEST_SETTINGS is not None:
            args += ['--ds {}'.format(DJANGO_TEST_SETTINGS)]
        elif DJANGO_SETTINGS is not None:
            args += ['--ds {}'.format(DJANGO_SETTINGS)]

    if not sugar:
        args += ['-p no:sugar']

    if verbose >= 1:
        args += ['-v']
    if verbose >= 2:
        args += ['--full-trace']

    if show_locals:
        args += ['-l']

    if plugins:
        for plug_name in plugins:
            if not plug_name.strip():
                continue

            if plug_name.startswith('-'):
                args += ['-p no:{}'.format(plug_name[1:])]
            else:
                args += ['-p {}'.format(plug_name)]

    test_config = {'paths': SRC_PATH}
    if test_type is not None:
        test_config = TEST_TYPES.get(test_type)
        mark = test_config.get('mark')

        if mark:
            args += ['-m "{}"'.format(mark)]

    with shell_env(PYTHONPATH=SRC_DIR):
        test_paths = test_config['paths'] or []
        test_paths = [conf.proj_path(p) for p in test_paths]
        local('pytest -c {conf} {args} {paths}'.format(
            conf=PYTEST_CFG_PATH,
            args=' '.join(args),
            paths = fs.surround_paths_with_quotes(test_paths)
        ))
