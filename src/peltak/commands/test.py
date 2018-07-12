# -*- coding: utf-8 -*-
"""
Testing commands
"""
from __future__ import absolute_import, unicode_literals
from . import cli, click


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
    import sys
    import os.path
    from peltak.core import conf
    from peltak.core import fs
    from peltak.core import shell

    build_dir = conf.get_path('BUILD_DIR', '.build')

    pytest_cfg_path = conf.get_path('PYTEST_CFG_PATH', 'ops/tools/pytest.ini')
    test_types = conf.get('TEST_TYPES', {})

    coverage_out_path = os.path.join(build_dir, 'coverage')
    coverage_cfg_path = conf.get_path('COVERAGE_CFG_PATH',
                                      'ops/tools/coverage.ini')

    django_settings = conf.get('DJANGO_SETTINGS', None)
    django_test_settings = conf.get('DJANGO_TEST_SETTINGS', None)

    src_dir = conf.get_path('SRC_DIR')
    src_path = conf.get_path('SRC_PATH')
    plugins = plugins.split(',')
    args = []

    if not no_coverage:
        args += [
            '--durations=3',
            '--cov-config={}'.format(coverage_cfg_path),
            '--cov={}'.format(src_path),
            '--cov-report=term:skip-covered',
            '--cov-report=html:{}'.format(coverage_out_path),
        ]

    if junit:
        args += ['--junitxml={}/test-results.xml'.format('.build')]

    if '-django' not in plugins:
        if django_test_settings is not None:
            args += ['--ds {}'.format(django_test_settings)]
        elif django_settings is not None:
            args += ['--ds {}'.format(django_settings)]

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
        test_config = test_types.get(tests_type)
        mark = test_config.get('mark')

        if mark:
            args += ['-m "{}"'.format(mark)]

    test_paths = test_config['paths'] or []
    test_paths = [conf.proj_path(p) for p in test_paths]
    result = shell.run(
        'pytest -c {conf} {args} {paths}'.format(
            conf=pytest_cfg_path,
            args=' '.join(args),
            paths=fs.surround_paths_with_quotes(test_paths)
        ),
        env={'PYTHONPATH': src_dir},
        exit_on_error=False
    )

    if result.failed and not (allow_empty is True and result.return_code == 5):
        sys.exit(result.return_code)
