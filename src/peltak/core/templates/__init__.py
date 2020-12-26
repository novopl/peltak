# Copyright 2017-2020 Mateusz Klos
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
.. module: peltak.core.templates
    :synopsis: Jinja2 templates support.

#########################
Script template reference
#########################


Using jinja filters
~~~~~~~~~~~~~~~~~~~

Let's suppose you have a scripts that runs pytest over your project and you want
to pass the verbosity flag down to the pytest command. The verbosity option
can be accessed with ``{{ opts.verbose }}`` but it is an ``int`` so we need
to somehow convert it to the appropriate flag ``-v``, or ``-vv`` etc. Thankfully
peltak already implements a filter to do just that, it's called ``count_flag``
and will convert a given number **N** to a flag that has the given letter appear
**N** times. Here's a quick example.


.. code-block:: yaml

    scripts:
        test:
            about: Run tests with pytest
            command: |
                pytest {{ opts.verbose | count_flag('v') }} {{ conf.src_dir }}

This will result in the following command being invoked:

.. code-block:: bash

    peltak run test
    # will result in: pytest src

    peltak run test -v
    # will result in: pytest src -v

    peltak run test -vv
    # will result in: pytest src -vv

Template context
================

Peltak will inject the following context into the template.

================== ================================================================
 Name               Description
------------------ ----------------------------------------------------------------
 ``conf``           | The entire configuration object. This is the dictionary
                    | representation of `pelconf.yaml` and makes it easy to acess
                    | any global configuration values from within a script.
 ``opts``           | Script command line options. This will contains all command
                    | line options the script was called with.
 ``script``         | The script configuration as read from `pelconf.yaml`.
                    | This will only contain the configuration for the currently
                    | running script, not the entire **scripts:** section.
 ``ctx``            | Current runtime context. This is a value store that exists
                    | only when peltak is running and is recreated on every run.
                    | This is a way to share runtime information between commands
                    | (things like **verbosity** or **pretend**).
 ``proj_path``      | A helper function. Given any project relative path (relative
                    | to `pelconf.yaml`) it will convert it to an absolute path.
================== ================================================================

On top of all the values in the context, you can also use
`/reference/script_filters`.


Dev Reference
=============

.. autoclass:: peltak.core.templates.Engine
    :members:

"""
from .engine import Engine  # noqa: F401
