###########################################
peltak - Simplify your day-to-day dev tasks
###########################################


Table of Contents
=================

.. toctree::
    :maxdepth: 2

    guides/_index
    reference/_index
    dev/_index


About peltak
============


Goals
~~~~~

.. include:: ../../README.rst
    :start-after: readme_about_start
    :end-before: readme_about_end

The way **peltak** tackles this problem is to try and create an invocation layer
between the developer and different 3rd party tools. The requirements we set
for ourselves are:

- **Simple by default**. The app should be useful for small projects where
  things are simple. You do not need to have a big, complex project for
  **peltak** to provide you with value. This means that the basic setup has
  to be as simple as possible.
- **Extensible**. It has to be easy to extend and still be useful when the
  project grows. This is the biggest drawback of shell scripts - with time
  they are either too simple to handle all cases or get so complex that
  maintaining them becomes hell for anyone but the orignal author.
- **Full auto-completion.** Once you get used to a tool, auto-completion
  becomes a second nature and can speed up your workflow considerably.
- **Easy command discovery and self help**.  This means the user can see what
  commands he can execute without having access to any manuals or guides. The
  way we achieve that is through implementing the ``--help`` flag on every
  command and sub command in peltak. This way you can always append ``--help``
  to your invocation and see what's available.


Simple by default
~~~~~~~~~~~~~~~~~

**peltak** comes with a small set of built-in commands that provide for a very
flexible base for simple projects. You can initialize a new peltak configuration
(`pelconf.yaml`) in the current project with::

    peltak init

This will ask you a few simple questions and you're ready to go. This will
generate very basic **peltak** configuration:

.. code-block:: yaml

    # peltak configuration file
    # Visit https://novopl.github.io/peltak for more information
    pelconf_version: '1'

    # Extra commands enabled. You can add local project commands, peltak built-ins
    # or 3rd party packages here.
    commands:
      - peltak.extra.git
      - peltak.extra.gitflow

    # This directory will be added to sys.path when the config is loaded.
    # Useful if do not keep the source code in th root directory.
    src_dir: "{src_dir}"

    # Scripts to help you manage your project. You can create as many scripts you
    # want.
    scripts:
      test:
        about: Test your code
        command: |
          echo "Change me, to run your tests"


This is a good starting point for your project. It will load few basic commands
for git and gitflow. There's also a stub for your first script. You can invoke
the test script with ``peltak run test`` and you can add as many scripts to your
configuration as you want (they do have to have unique names though).


Extensible
~~~~~~~~~~

**peltak** is designed to grow with your project and provides a few layers of
functionality that allow you to start small just like with simple shell scripts
(but with more capabilities). For that there is the ``scripts:`` section in
`pelconf.yaml`. You can define shell scripts that can make use of a very
flexible templating engine. For most projects this will actually be enough.
**peltak** allows you to easily define cmd line options for your scripts and
thanks to the templating support you can actually dynamically build your script
based on configuration and command line options. You can read more on how to
use scripts in `/guides/scripts`.

If you need more functionality, **peltak** also makes it very easy to extend
the default set of commands with python. If your project suddenly needs
something more complicated, or to link to your existing tools you can write
a new peltak command with few lines of python and thanks to the way the app
is designed you can use it in your project right away. You can find more
information about creating custom peltak commands in
`/guides/create_custom_commands`.

In fact, the way the commands are implemented, makes it also very easy to turn
them into packages. If you find out that there is a lot of peltak commands that
overlap between your projects it might be a good idea to turn them into a
library and use it with each project. Even better if you can open source your
code and let others use it in their projects too. We created a helper guide on
how to create packages for peltak commands if you need more information:
`/guides/package_commands`.

**peltak** is designed to be possibly least intrusive. Even if your team decides
not to use it, you can use it yourself, just don't commit the `pelconf.yaml`
file and you will be good. This way you can have a smooth developer experience
on every project you work on.

Auto-completion
~~~~~~~~~~~~~~~

