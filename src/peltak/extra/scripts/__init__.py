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
#####################
Create peltak scripts
#####################

.. module: peltak.extra.scripts
    :synopsis: Custom project scripts

**peltak** supports defining simple scripts directly inside `pelconf.yaml`. On
top of just defining the command, by default the command is processed by jinja
before it's being ran. This makes it possible to inject some dynamic values into
the command and makes the whole scripts subsystem very flexible.


Get a list of scripts available in the project
==============================================

To get a list of all scripts that are defined in `pelconf.yaml` you only need
to run the ``peltak run`` command without any arguments. Here's an example from
the **peltak** project itself (at the time of writing)::

    $ peltak run
    Usage: peltak run [OPTIONS] COMMAND [ARGS]...

      Run custom scripts

    Options:
      --help  Show this message and exit.

    Commands:
      checks       Run all checks (types, pep8, code style)
      cov-core     Generate coverage report for peltak.core
      cov-extra    Generate coverage report for peltak.extra
      cov-scripts  Generate coverage report for peltak.extra.scripts
      docs         Generate sphinx documentation
      tests        Run unit tests
      type-check   Run static type checks


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


Debugging your script
~~~~~~~~~~~~~~~~~~~~~

**peltak** provides a few helpers to ease the process of creating custom
project scripts. The first one is the ``--pretend`` option. Providing it when
invoking your script will cause **peltak** to render the compiled template
script instead of running it. This allows you to see exactly what command would
be executed.

The second one is the ``-v``, ``--verbose`` flag. With verbosity level 3 (``-vvv``)
**peltak** will render the full script template context as a highlighted YAML.
This makes it very easy to see exactly what values are available in the template
context of your project.

Combining ``--pretend`` with ``-vvv`` will show you the full template context
followed by a compiled command without executing anything. This is perfect when
you're working on your script and are afraid you might break something.


Multiline and multi statement commands
======================================

The *test* command above is a very simple one. What if your script command is
very long, or you want to call multiple shell commands? The command you define
is treated as a shell script, so you can do whatever you can with shell scripts.
One thing to remember is to use ``set -e`` in your script if you want it to fail
if any of the commands fail.

For convenience, you can use the YAML multiline string syntax:

.. code-block:: yaml

    checks:
        about: Run checks on the code base
        command: |
            set -e
            pipenv run mypy src
            pipenv run pep8 --config tools/pep8.ini src
            pipenv run pylint --rcfile tools/pylint.ini src


Templating capabilities of scripts
==================================

The scripts module was designed to parse the commands as templates and inject
**peltak's** current working environment. This means you can use configuration
and some helper filters to generate the actual command.

If you want to more details about templating in scripts, you can read
`/reference/script_templates`.

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

You can find out more in `/reference/script_filters`

"""
from .commands import run_cli
