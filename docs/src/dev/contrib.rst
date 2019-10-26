####################################
Setup up the project for development
####################################

.. code-block:: shell

    $ git clone git@github.com:novopl/peltak.git
    $ cd peltak
    $ virtualenv env
    $ source ./env/bin/activate
    $ pip install -r requirements.txt -r ops/devrequirements.txt
    $ peltak git add-hooks

.. note::
    The CircleCI builds can be found
    `here <https://circleci.com/gh/novopl/peltak>`_


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
