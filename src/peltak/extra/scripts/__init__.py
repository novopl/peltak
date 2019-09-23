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

######################
Custom project scripts
######################

**peltak** supports defining simple scripts directly inside `pelconf.yaml`. On
top of just defining the command, by default the command is processed by jinja
before it's being ran. This makes it possible to inject some dynamic values into
the command and makes the whole scripts subsystem very flexible.

How to enable ``peltak run`` command
====================================

You need to specify it in your **commands:** section in `pelconf.yaml`:

.. code-block:: yaml

    commands:
        - peltak.extra.scripts


Defining a script
=================

You can define a script inside `pelconf.yaml` in the **scripts:**. The script
always has a name (key in the scripts config section) and a command (required
prop). Say you want to define a ``test`` command that invokes pytest on the
``./test`` directory, here's the corresponding `pelconf.yaml` section.

.. code-block:: yaml

    scripts:
        test:
            command: pytest ./test

And you can run this command with:

.. code-block:: bash

    peltak run test

Multiline and multi statement commands
======================================

The *test* command above is a very simple one. What if your script command is
very long, or you want to call multiple shell commands? You can leverage the
bash syntax and just separate the commands with semicolons. Here's a little
example:

.. code-block:: yaml

    checks:
        about: Run checks on the code base
        command: |
            pipenv run mypy src;
            pipenv run pep8 --config tools/pep8.ini src;
            pipenv run pylint --rcfile tools/pylint.ini src;


Templating capabilities of scripts
==================================

The scripts module was designed to parse the commands as templates and inject
**peltak's** current working environment. This means you can use configuration
and some helper filters to generate the actual command.

.. note::
    Scripts templating is very simple. It should be used only for simple
    value substitution with optional processing. If need flow control for a
    script you probably should look at implementing a custom peltak command for
    the project as this will give you the full power of python and is also a
    very simple to do.

Injecting config values from `pelconf.yaml` into your script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's modify our *checks* command to use config variables. We're repeating
ourselves passing ``src`` to every command. You probably already have a
``src_dir`` variable set up in your config, why not use that to execute the
checks? Same goes for the location of the tools config files. We can create
a new config variable to store the tool config dir and just use it in
our command. The current configuration is injected into the template as ``conf``
object. You can access it via the ``{{ EXPRESSION }}`` syntax. Here's a
modified version of the *checks* command.

.. code-block:: python

    src_dir: src
    tool_dir: tools

    checks:
      about: Run checks on the code base
      command: |
        pipenv run mypy {{ conf.src_dir }}
        pipenv run pep8 --config {{ conf.tool_dir }}/pep8.ini {{ conf.src_dir }};
        pipenv run pylint --rcfile {{ conf.tool_dir }}/pylint.ini {{ conf.src_dir }};

This makes it easy to reuse certain values between scripts as all scripts can
access config through ``{{ conf.VALUE }}`` expression. This makes managing the
project much easier as `pelconf.yaml` can serve as a config store for all
scripts and changing any of those values will work right away with all scripts
that use it.

Using jinja filters
~~~~~~~~~~~~~~~~~~~

Let's suppos you have a scripts that runs pytest over your project and you want
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

"""
from .commands import run_cli
