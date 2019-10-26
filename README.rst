######
peltak
######

.. readme_about_start

**peltak**'s goal is to simplify day-to-day dev tasks that we all, as developers,
have to do. It does not try to be a build system or to replace any of the tools
you would normally use when developing project like test runners, linters, etc.
Think of it rather as a replacement for the shell scripts that usually wrap
those tools. It actually started years ago as a collection of those shell
scripts that with time evolved into a very flexible, extensible and easy to use
command line app.

.. readme_about_end

Useful links
============

- `Documentation <https://novopl.github.io/peltak>`_
    - `Installation <https://novopl.github.io/peltak/docs/html/guides/installation.html>`_
    - `Quickstart <https://novopl.github.io/peltak/docs/html/guides/quickstart.html>`_
    - `Dev Docs <https://novopl.github.io/peltak/docs/html/dev/_index.html>`_
- `Source Code <https://github.com/novopl/peltak>`_
- `CI Builds <https://circleci.com/gh/novopl/peltak>`_


Installation
============

.. readme_installation_start

.. code-block:: shell

    $ pip install peltak

Enabling auto-completion
------------------------
**peltak** has a great auto-completion thanks to the underlying click library.
The steps to enable it vary slightly depending on what shell you are using

**Bash users**

    Either run this command or to make the change permanent add it to your
    ``~/.bashrc``:

    .. code-block:: shell

        eval "$(_PELTAK_COMPLETE=source peltak)"

**ZSH users**
    Either run this command or to make the change permanent add it to your
    ``~/.zshrc``:

    .. code-block:: shell

        eval "$(_PELTAK_COMPLETE=source_zsh peltak)"

.. readme_installation_end
