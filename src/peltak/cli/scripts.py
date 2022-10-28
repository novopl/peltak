"""
##############
``peltak run``
##############


Dev Docs
========

What need to be done?
~~~~~~~~~~~~~~~~~~~~~

.. uml::

    @startwbs
    * Scripts support
    ** Render command template
    *** Config values
    *** Env variables
    *** command line options
    ** click integration
    *** Display about command as help
    *** Autocomplete script names
    @endwbs


Configuration
~~~~~~~~~~~~~

Options for a single script

.. code-block:: yaml

    scripts:
      checks:
        about: Run checks on the code base
        accepts_files: True
        command: |
          mypy {{files}}; \\
          pycodestyle --config ops/tools/pep8.ini {{files}}; \\
          pylint --rc-file ops/tools/pylint.ini {{files}};




Example
-------

.. code-block:: yaml

    scripts:
      build-docs:
        about: Generate sphinx documentation
        command: |
          sphinx-refdoc  \\
            -i src/peltak \\
            -i src/peltak_appengine \\
            -i src/peltak_django \\
            -i src/cliform \\
            {{opts.verbosity | count_flag('-v')}} \\
            docs/ref; \\
            \\
          sphinx-build \\
            -b html \\
            -d {{cfg.build_dir}}/docs \\
            docs \\
            docs/html

      unit-tests:
        about: Run unit tests
        command: |
          pytest -c ops/tools/pytest.ini \\
            --cov-config=ops/tools/coverage.ini \\
            --cov={{cfg.src_dir}} \\
            --cov-report=term \\
            --cov-report=html:.build/coverage \\
            --junitxml={cfg.build_dir}/test-results.xml \\
            --full-trace \\
            -vvv \\
            test/unit

      checks:
        about: Run checks on the code base
        command: |
          mypy {{files}}; \\
          pycodestyle --config ops/tools/pep8.ini {{files}}; \\
          pylint --rc-file ops/tools/pylint.ini {{files}};
"""
from pathlib import Path

from peltak.cli import peltak_cli
from peltak.core import conf, hooks
from peltak.core.scripts import loader


@peltak_cli.group('run')
def run_cli():
    """ Run custom scripts """
    pass  # nocov


@hooks.register('post-conf-load')
def post_conf_load():
    """ After the config was loaded, register all scripts as click commands. """
    scripts_dir = Path(conf.get_path('scripts_dir', 'scripts'))

    loader.register_scripts_from(scripts_dir)
