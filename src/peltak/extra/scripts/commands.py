# -*- coding: utf-8 -*-
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
from __future__ import absolute_import

from peltak.commands import root_cli, pretend_option
from peltak.core import hooks
from peltak.core import util


@root_cli.group('run')
@pretend_option
@util.mark_experimental
def run_cli():
    # type: () -> None
    """ Run custom scripts """
    pass


@hooks.register('post-conf-load')
def post_conf_load():
    """ After the config was loaded, register all scripts as click commands. """
    from peltak.core import conf
    from . import logic

    # This allows defining script options and attaching them to the click
    # command. The drawback is that it does slow auto completion and it might
    # be too slow if we have a lot of scripts. Having one command that just
    # runs the scripts would be probably faster, but won't support custom
    # script options.
    scripts = conf.get('scripts', {})
    for name, script_conf in scripts.items():
        script = logic.Script.from_config(name, script_conf)
        script.register(run_cli)
