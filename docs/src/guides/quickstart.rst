##########
Quickstart
##########

In this guide, we will walk through an example flask project and how can you use
**peltak** to manage it. Our app will be a very simple simple TODO app API.

Configure test runner with peltak
=================================

In our `pelconf.yaml` configuration, we will define a **test** script that will
run all of our unit test with some default configuration:

.. code-block:: yaml

    pelconf_version: '1'

    scripts:
      test:
        about: Run unit tests
        command: |
          pytest test/unit

This is the simplest version of that command, but it will only tell us whether
the tests passed or not. It would be nice if we could also generate coverage
report and see the slowest tests (so we can quickly see if some tests take
suspiciously large amount of time to execute). Here's the full setup for tests:

.. literalinclude:: /examples/quickstart/pelconf.yaml
    :language: yaml
    :lines: 3,5-6,21,26-27,29-35

As you can see, we defined an extra config value **build_dir**. Right now we use
it only in one place so it might not be necessary, but once we start integrating
other tools, we can share that value so it's easier to maintain and change in the
future (if needed). This also shows how easy it is to define your own config
values and use them in your scripts.

Now you can run tests in your projects with a simple command::

    peltak run test


We can actually make it even more simple, by attaching our script to the root
**peltak** command. To do so, we only need to set ``root_cli`` to **true** in
our script config:


.. literalinclude:: /examples/quickstart/pelconf.yaml
    :language: yaml
    :lines: 3,5-6,21,26-35


Now you can run your script with::

    peltak test


Configure code check tools (linters) with peltak
================================================

Another thing you would probably use on a project are various code checkers.
Often times you will have more than one. One of the issues you might run into
is how different tools handle filtering files. It might be the case you need to
write 2 sets of completely different file filters just to get the same file
list as a result. **peltak** comes with a built in method of filtering files
and injecting them into your scripts. This way you can bypass the built-in
filters and just pass the pre-filtered list of files to any of the tools you use
in your script.

To use it, you have to define a ``files:`` section in your script config where
you define filtering rules. Then in your script you will have a ``{{ files }}``
template variable that you can use. This is a list of strings, so be careful
how you pass at to your tools. There is a built-in filter
`wrap_paths` to help you with getting the files
ready to pass to a command line. It will wrap all items in the given array with
double quotes, making sure you don't have unexpected errors due to paths having
spaces, etc.

Here's an example of pylint + mypy based lint script:


.. literalinclude:: /examples/quickstart/pelconf.yaml
    :language: yaml
    :lines: 3,5-6,21,37-50


Using git-flow with peltak
==========================

**peltak** comes bundled with few commands that implement the full git-flow.
Those can be a real help if you and your team are using git-flow. The commands
themselves have a pretty straightforward implementation as well so if you would
like to automate a different kind of work-flow your team is using, looking at
the `peltak.extra.gitflow` commands implementation can be a good start in
implementing your own commands.

The git-flow commands are not enabled by default. You need to explicitly enable
them using the ``commands:`` section in `pelconf.yaml`:

.. code-block:: yaml

    pelconf_version: '1'

    commands:
      - peltak.extra.gitflow

If you have used ``peltak init`` to generate the initial configuration than
those the gitflow commands will be enabled for you already.

There are 3 main command groups: **feature**, **release** and **hotfix**.
Each of them has a set of commands to manage the given branch (be it *feature*,
*hotfix* or *release*). The commands are:

``start``
    Will create the branch. The *feature/* and *release/* branches must always
    be created from the develop branch and the *hotfix/* branches from the
    *master* branch. When creating the *feature* and *hotfix* branch it will
    ask you the feature name and create a branch in format
    ``feature/<feature_name_in_lowercase_underscore>``. The release branch will
    always be ``release/<released_ver>``.

``merged``
    This command will cleanup after the given branch is merged remotely (eg on
    github). This will:

    1. Checkout the target branch
    2. Pull the merged changes,
    3. delete the merged branch locally
    4. run `git fetch --prune` to remove the references to the merged remote
       branch.

``finish``
    This will merge the branch locally and cleanup:

    1. Checkout the target branch
    2. Merge the branch we want to merge (be it **feature**, **hotfix** or
       **release**.
    3. Delete the merged branch

Feature life-cycle
~~~~~~~~~~~~~~~~~~

Let's see how we would manage a git-flow feature branch with **peltak**.

Release life-cycle
~~~~~~~~~~~~~~~~~~

