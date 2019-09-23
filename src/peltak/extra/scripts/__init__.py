# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""

#######################################
``peltak run`` - Custom project scripts
#######################################

What need to be done?
=====================

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
=============

Options for a single sciript

.. code-block::yaml

    scripts:
      checks:
        about: Run checks on the code base
        accepts_files: True
        command: |
          mypy {{files}}; \\
          pycodestyle --config ops/tools/pep8.ini {{files}}; \\
          pylint --rc-file ops/tools/pylint.ini {{files}};




Example
~~~~~~~

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
from .commands import run_cli
