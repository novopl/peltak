
######
peltak
######

.. readme_inclusion_marker

**peltak** is a command line tool to automate a lot of project related tasks.
The tool should only wrap up existing project tools and not try to replace them.
Also when implementing new commands lean towards just calling external tools
rather than interfacing through the API. This way the commands implementation
should resemble shell scripts in their structure and also serve as a reference
on how to call the respective 3rd party tool without the use of **peltak**.
Docker commands are a good example here as docker has a great python support
but reading through the command implementation you know exactly what to do to
do it manually and you probably don't even have to know python.

**WARNING: Beta:** The project is mainly lacking good documentation and
tutorials. The commands themselves are documented quite well, but there is
no generic documentation or guides on how to extend and customize peltak.

Right now only ``peltak.core`` is unit tested. The commands themselves are
tested manually in multiple projects that use peltak for day to day management
and CI runs. Before 1.0, the commands implementation should also be unit tested.
Only the CLI interface shouldn't (e2e tests for that if any).

.. note::
    The CircleCI builds can be found
    `here <https://circleci.com/gh/novopl/peltak>`_

Installation
============

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


Contributing
============

Setting up development repo
---------------------------

.. code-block:: shell

    $ git clone git@github.com:novopl/peltak.git
    $ cd peltak
    $ virtualenv env
    $ source ./env/bin/activate
    $ pip install -r requirements.txt -r ops/devrequirements.txt
    $ peltak git add-hooks


Running tests
.............

**Config**: The types of tests are defined in ``pelconf.py`` and the
pytest configuration is defined in ``ops/tools/pytest.ini``.

.. code-block:: shell

    $ peltak test

.. admonition:: **How to test for all supported python versions?**

    To run tox you need to first generate the requirements files. You
    can do this with ``pipenv lock -d --requirements > requirements.txt``. Once
    it's done, you can just run ``tox`` to test against python2.7, python3.4
    and python3.6 all in one go.

Linting
.......

**Config**: The list of locations to lint is defined in ``pelconf.py`` and the
linters configuration is defined in ``ops/tools/{pylint,pep8}.ini``.

.. code-block:: shell

    $ peltak lint

Generating docs
...............

**Config**: The list of documented files and general configuration is in
``pelconf.py`` and the Sphinx configuration is defined in ``docs/conf.py``.

.. code-block:: shell

    $ peltak docs
