######################
Custom peltak commands
######################

.. note::

    You can find the example code for this tutorial here:
    `here <https://github.com/novopl/peltak/tree/master/docs/src/examples/custom_commands>`_

Background
==========

When the built in scripts functionality is not enough **peltak** allows you to
write commands directly in python. You are free to keep your **peltak** commands
as part of your project or move them to a separate directory. You always need
to specify what commands are available within your project's **pelconf.yaml** so
from **peltak's** perspective it really doesn't matter where you store them.

The rule of thumb is to start with project specific commands being stored as
part of the project repo and as you progress you might extract some of your
commands into a separate packages so you can reuse them in other projects or
just share with the community.

**peltak** internally uses `click <https://click.palletsprojects.com/en/7.x/>`_
so everything you can find in the click docs applies here as well. **peltak**
does provide some functionality built on top of click that makes some of the
tasks easier to implement (`pretend_option` for example), and already provides
the root CLI group (`peltak.commands.root_cli`) as well as some predefined
groups that you can extend.

You can attach your commands to any existing group as well as create new groups
and attach them wherever you want. **peltak** tries to be very flexible in terms
of how you structure the CLI commands for your project.


How to create custom commands
=============================

Hello world command
~~~~~~~~~~~~~~~~~~~

Let's start with the most basic command that will just print hello world to
the terminal. This will show you all the steps you need to take to implement the
command and make it available to peltak. Let's initialize a new
`pelconf.yaml` with ``peltak init``:

.. code-block:: bash

    peltak init --blank -v

.. note::

    The generated `pelconf.yaml` should look like this:

    .. literalinclude:: /examples/custom_commands/pelconf.yaml
        :language: yaml
        :lines: 1-7,9-


The next step is to create the python module with the commands. It has to be
importable by peltak so needs to be inside whatever ``src_dir`` in `pelconf.yaml`
is set to. Let's create a new file called ``./custom_commands.py``:

.. literalinclude:: /examples/custom_commands/custom_commands.py
    :lines: 1-7

For peltak to be able to load your command file you need to add it to your
``commands:`` section in `pelconf.yaml`:

.. literalinclude:: /examples/custom_commands/pelconf.yaml
    :language: yaml

Now our new command is visible to peltak and we can execute it with:

.. code-block:: bash

    $ peltak hello-world
    Hello, World!


A more advanced example
~~~~~~~~~~~~~~~~~~~~~~~

As a more advanced example, we will re-implement the **lint** script defined
in the `/guides/quickstart` guide. First let's define the command itself along
with it's options to match the ``files:`` section so we can filter the files
that will be linted:

.. literalinclude:: /examples/custom_commands/custom_commands.py
    :lines: 1-45,47-54

.. warning::

    Try not to import anything at the top module level in the module that
    defines commands. Only things that are required to define the command (and
    it's arguments) should be imported at top level.

    This is due to the fact that all command modules need to be imported during
    shell completion, so the more they import globally the slower the
    completion gets. This might not be an issue with just one module
    misbehaving, but if that laziness spreads it quickly becomes noticeable and
    hurts user experience.

    Ideally you want to have a separate module with the implementation of each
    command you export. The click command handlers just import that code inside
    the command handler. This way the import won't happen until the command
    is actually executed and it keeps the command file size small for faster
    parsing.

Now we will create a new file with the business logic behind our lint command.
In this tutorial we will call it `custom_commands_lint.py` but you can use
whatever structure you like.

.. literalinclude:: /examples/custom_commands/custom_commands_logic.py

The last bit is to actually call our lint function from our peltak command:


.. literalinclude:: /examples/custom_commands/custom_commands.py
    :lines: 43-
