.. readme_badges_start

|circleci| |nbsp| |codecov| |nbsp| |mypy| |nbsp| |license| |nbsp| |py_ver|


.. |circleci| image:: https://circleci.com/gh/novopl/peltak-changelog.svg?style=shield
             :target: https://circleci.com/gh/novopl/peltak-changelog
.. |codecov| image:: https://codecov.io/gh/novopl/peltak-changelog/branch/master/graph/badge.svg?token=SLX4NL21H9
            :target: https://codecov.io/gh/novopl/peltak-changelog
.. |mypy| image:: https://img.shields.io/badge/type_checked-mypy-informational.svg
.. |license| image:: https://img.shields.io/badge/License-Apache2-blue.svg
.. |py_ver| image:: https://img.shields.io/badge/python-3.7+-blue.svg
.. |nbsp| unicode:: 0xA0

.. readme_badges_end

################
peltak-changelog
################

.. readme_about_start


This package adds the commands that allow you to greatly reduce the amount of
work required in maintaining a change log for your releases. The main command
**peltak changelog** will parse all commits since the last release and extract
all features/changes/fixes implemented. To achieve this, it will look for
specific tags in the commit descriptions. Once all those are found it will print
a nice change log. Here's an example::

    $ peltak changelog
    v0.21.2

    Features:
    - A description of a feature, taken from the commit message
    - Each feature has it's own list item
    - And each commit can have multiple features and/or fixes defined

    Changes:
    - One thing had to be change to something else.
    - Another thing also had to be changed.

    Fixes:
    - Description of the first fix
    - Each fix has it's own list item

.. readme_about_end


Links
=====

* `Documentation`_

    * `Contributing`_
    * `Reference`_


.. _Documentation: https://novopl.github.io/peltak-changelog
.. _Contributing: https://novopl.github.io/peltak-changelog/pages/contributing.html
.. _Reference: https://novopl.github.io/peltak-changelog/pages/reference.html


Installation
============

.. readme_installation_start

With ``pip``
~~~~~~~~~~~~

.. code-block:: shell

    $ pip install peltak-changelog

With ``poetry``
~~~~~~~~~~~~~~~

.. code-block:: shell

    $ poetry add peltak-changelog

.. readme_installation_end


Overview
========

.. readme_overview_start

Commit format
~~~~~~~~~~~~~

.. code-block:: text

    <title>

    <description text>

    (<tag>) <feature description>

    <description text>

Commit message example
----------------------

.. code-block:: text

    Just added some new cool feature

    (feature) This feature allows the user to do many
    great things.
    (fix) This feature also fixes some issues we had
    before

    Closes #1


Configuration
~~~~~~~~~~~~~

The command can be configured in the project configuration file (``peltak.yaml``).
You can define what tags are searched and what is their corresponding header in
the changelog. Here is an example (this is the default configuration):

.. code-block:: yaml

    changelog:
      tags:
        - header: 'Features'
          tag: 'feature'
        - header: 'Changes'
          tag: 'change'
        - header: 'Fixes'
          tag: 'fix'

.. readme_overview_end
