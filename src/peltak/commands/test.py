# -*- coding: utf-8 -*-
"""
Testing commands
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
import os.path

# 3rd party imports
import click

# local imports
from peltak.core import conf
from peltak.core import fs
from peltak.core import shell
from . import cli


BUILD_DIR = conf.get_path('BUILD_DIR', '.build')

PYTEST_CFG_PATH = conf.get_path('PYTEST_CFG_PATH', 'ops/tools/pytest.ini')
TEST_TYPES = conf.get('TEST_TYPES', {})

COVERAGE_OUT_PATH = os.path.join(BUILD_DIR, 'coverage')
COVERAGE_CFG_PATH = conf.get_path('COVERAGE_CFG_PATH', 'ops/tools/coverage.ini')

DJANGO_SETTINGS = conf.get('DJANGO_SETTINGS', None)
DJANGO_TEST_SETTINGS = conf.get('DJANGO_TEST_SETTINGS', None)


@cli.command()
@click.option('--no-sugar', is_flag=True)
@click.option('--type', 'tests_type', type=str, default='default')
@click.option('-v', '--verbose', count=True)
@click.option('--junit', is_flag=True)
@click.option('--no-locals', is_flag=True)
@click.option('--no-coverage', is_flag=True)
@click.option('--allow-empty', is_flag=True)
@click.option('--plugins', type=str, default='')
def test(
        no_sugar, tests_type, verbose, junit, no_locals,
        no_coverage, plugins, allow_empty
):
    """ Run all tests against the current python version. """
    src_dir = conf.get_path('SRC_DIR')
    src_path = conf.get_path('SRC_PATH')
    plugins = plugins.split(',')
    args = []

    if not no_coverage:
        args += [
            '--durations=3',
            '--cov-config={}'.format(COVERAGE_CFG_PATH),
            '--cov={}'.format(src_path),
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

    if no_sugar:
        args += ['-p no:sugar']

    if verbose >= 1:
        args += ['-v']
    if verbose >= 2:
        args += ['--full-trace']

    if not no_locals:
        args += ['-l']

    if plugins:
        for plug_name in plugins:
            if not plug_name.strip():
                continue

            if plug_name.startswith('-'):
                args += ['-p no:{}'.format(plug_name[1:])]
            else:
                args += ['-p {}'.format(plug_name)]

    test_config = {'paths': src_path}
    if tests_type is not None:
        test_config = TEST_TYPES.get(tests_type)
        mark = test_config.get('mark')

        if mark:
            args += ['-m "{}"'.format(mark)]

    test_paths = test_config['paths'] or []
    test_paths = [conf.proj_path(p) for p in test_paths]
    result = shell.run(
        'pytest -c {conf} {args} {paths}'.format(
            conf=PYTEST_CFG_PATH,
            args=' '.join(args),
            paths = fs.surround_paths_with_quotes(test_paths)
        ),
        env={'PYTHONPATH': src_dir},
        exit_on_error=False
    )

    if result.failed and not (allow_empty is True and result.return_code == 5):
        sys.exit(result.return_code)
