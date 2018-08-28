# -*- coding: utf-8 -*-
"""
Testing commands
"""
from __future__ import absolute_import
from . import cli, click


@cli.command('test')
@click.argument('tests_type', metavar='<type>', type=str, default='default')
@click.option(
    '-v', '--verbose',
    count=True,
    help=("Be verbose. Can specify multiple times for more verbosity. This "
          "will also influence the verbosity of pytest output.")
)
@click.option(
    '--junit',
    is_flag=True,
    help="Write junit XML report to BUILD_DIR/test-results.xml."
)
@click.option(
    '--no-locals',
    is_flag=True,
    help="Disable pytest printing the values of local variables."
)
@click.option(
    '--no-coverage',
    is_flag=True,
    help="Disable code coverage generation."
)
@click.option(
    '--allow-empty',
    is_flag=True,
    help="Do not return non-zero code if the test suite is empty."
)
@click.option(
    '--plugins',
    type=str,
    default='',
    help=("Comma separated list of pytest plugins to activate. If the name "
          "of the plugins starts with '-' it will be disabled, otherwise it "
          "will be enabled.")
)
def test(
        tests_type, verbose, junit, no_locals, no_coverage, plugins, allow_empty
):
    """ Run tests against the current python version.

    This command uses pytest internally and is just a thing wrapper over it
    to simplify most common tasks. You can define multiple test types where
    a test type is a combination of paths to test and pytest marker definition
    for the test run. This allows to split tests with fine granularity and
    and run them easily. You need at least one TEST_TYPE to run the tests. The
    test type *default* will be used as default if no type is specified. If
    there is no configuration for *default* it will run the tests in the
    directory specified by SRC_PATH conf variable.

    SRC_DIR is used as PYTHONPATH for the test runner. If you need to customize
    it, use that variable.

    The coverage report will be written to ``BUILD_DIR/coverage``.

    If your project is using django, you can use DJANGO_TEST_SETTINGS conf
    variable to specify which settings to use for the tests.

    Config Sample::

        \b
        conf.init({
            'COVERAGE_CFG_PATH': 'ops/tools/coverage',
            'DJANGO_TEST_SETTINGS': 'mypkg.settings.test',
            'TEST_TYPES': {
                'default': {'paths': ['test']},
                'no_django': {
                    'mark': 'not django',
                    'paths': ['test']
                }
            }
        })

    Examples::

        \b
        $ peltak test                   # Run tests using the default options
        $ peltak --no-sugar             # Disable pretty output
        $ peltak --junit                # Generate BUILD_DIR/test-results.xml
        $ peltak test --no-sugar -vv    # Be extra verbose

    """
    import sys
    import os.path
    from peltak.core import conf
    from peltak.core import log
    from peltak.core import fs
    from peltak.core import shell

    log.info("Running <33>{} <32>tests".format(tests_type))

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

    test_config = test_types.get(tests_type)
    if test_config is None:
        log.info("Test type configuration missing: '{}'".format(src_path))

        for possible_path in (conf.proj_path('test'), conf.proj_path('tests')):
            if os.path.exists(possible_path):
                test_config = {'paths': possible_path}
                break
        else:
            log.err("No tests detected. Configure your TEST_TYPES.")
            sys.exit(-1)

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

    log.info("To see the HTML coverage report browse to <34>file://{}".format(
        conf.proj_path('.build/coverage/index.html')
    ))

    if result.failed and not (allow_empty is True and result.return_code == 5):
        sys.exit(result.return_code)
