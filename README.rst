
######
fabops
######

.. readme_inclusion_marker

**fabops** is a set of fabric commands to help out manage a project. The
intention is to not use it as a dependency but rather directly clone the
`ops/commands<https://github.com/novopl/fabops-commands>`_ submodule into the
project and create a branch for the project.

The management commands should be tightly coupled with the project to suit its
particular needs. Having all changes to ``ops/commands`` on a branch makes it
easier to update the commands if something useful is released upstream. If
you're using this code inside an organisation, it would probably be wise to make
a fork and maintain common changes across your project in it. This way you can
have a customised version that can still be updated from mainstream. An added
bonus is that you're protected in an unlikely case when something happens with
the mainstream.

The commands are intentionally simple to avoid complexity in the project
management tools. This is mainly to standardize the set of actions performed
by developers. Ideally, all commands should be executable manually without the
help of **fabops**.


Installation
============

.. code-block:: shell

    $ pip install serafin


Contributing
============

Setting up development repo
---------------------------

.. code-block:: shell

    $ git clone git@github.com:novopl/sphinx-refdoc.git
    $ cd sphinx-refdoc
    $ virtualenv env
    $ source ./env/bin/activate
    $ pip install -r requirements.txt -r devrequirements.txt
