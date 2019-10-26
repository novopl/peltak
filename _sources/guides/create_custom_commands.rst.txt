######################
Custom peltak commands
######################

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
terminal. This will show you all the steps you need to take to implement the
command and make it available to peltak. We will assume that you keep all your
code inside a ``./src`` directory in your project. The `pelconf.yaml` file
will live in the project root.

For peltak to be able to load your command file you need to place it within
``src_dir`` as defined by `pelconf.yaml`. Here is an example config we will
start
