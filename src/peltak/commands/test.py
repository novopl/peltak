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
    help="Write junit XML report to build_dir/test-results.xml."
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
    and run them easily. You need at least one test type to run the tests. The
    test type *default* will be used as default if no type is specified. If
    there is no configuration for *default* it will run the tests in the
    directory specified by SRC_PATH conf variable.

    src_dir is used as PYTHONPATH for the test runner. If you need to customize
    it, use that variable.

    The coverage report will be written to ``build_dir/coverage``.

    If your project is using django, you can use django_test_settings conf
    variable to specify which settings to use for the tests.

    Config Sample::

        \b
        conf.init({
            'coverage_cfg_path': 'ops/tools/coverage',
            'django_test_settings': 'mypkg.settings.test',
            'test': {
                'types': {
                    'default': {'paths': ['test']},
                    'no_django': {
                        'mark': 'not django',
                        'paths': ['test']
                    }
                }
            }
        })

    Examples::

        \b
        $ peltak test                   # Run tests using the default options
        $ peltak --no-sugar             # Disable pretty output
        $ peltak --junit                # Generate build_dir/test-results.xml
        $ peltak test --no-sugar -vv    # Be extra verbose

    """
    from .impl import test
    test.test(
        tests_type, verbose, junit, no_locals, no_coverage, plugins, allow_empty
    )
