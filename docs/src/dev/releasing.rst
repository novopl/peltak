################################
Releasing new versions of peltak
################################


Current setup
=============

Currently the project is using gitflow to manage the code. All development happens
on the ``develop`` branch and all releases are built from ``master``. All work should
be merged into ``develop``.

Once the release is to be made, a new ``release/`` branch is created. It can be done
from the shell and you can also specify what kind of a version bump does the release
represent. The default is ``patch`` (_._.X) but can be set to ``minor`` (_.X.0)) or
``major`` (X.0.0)::

    peltak release start            # Start a patch release (1.2.3 -> 1.2.4)
    peltak release start patch      # Same as above
    peltak release start minor      # Start a minor release (1.2.3 -> 1.3.0)
    peltak release start major      # Start a major release (1.2.3 -> 2.0.0)

Once the release branch is created it need's to be pushed to the origin and a release
PR needs to be created. This can be easily done from shell::

    peltak git push
    peltak pr-release

Now you need to go to the PR, wait for the CI to build and merge the pull request.
Once that's done, the build on the master branch will release a new version to pypi,
as well as build a new version of the docs and deploy it to github pages.

One final step is to merge the release branch back into develop and delete the local
release branch. All of that can be done quickly via shell as well::

    peltak release merged

You should end up back on ``develop`` branch, ready to work on new features.


Desired setup
=============


Automatic Releases
~~~~~~~~~~~~~~~~~~

We want to simplify this process as it's both quite lengthy and generates a lot
of unnecessary merge commits thus cluttering the history. With the new approach
all development happens on master. Once the release is ready a release commit is
created and tagged appropriately. The CI is setup to have a release build and
deployment for the release tags. This way we decide what is released and we avoid
creating a lot of merge commits due to existence of the release branch.

Here's the proposed flow for releasing new versions::

    # at any point on the master branch
    peltak make-release patch
    git push

The first command (``peltak make-release``) should bump the project version,
create a release commit with the changelog and tag the release with the version tag.

For the release tag build on the CI, we should make sure the appropriate github
release is also created and that it contains the changelog.

Manual releases
~~~~~~~~~~~~~~~

With the new approach, we also want to be able to release manually from the CLI.
This should not be used frequently, but might be useful sometimes (especially
under problematic circumstances). In those cases, we also create the release
commit locally, but instead of pushing the code, we can release directly to pypi::

    peltak make-release minor
    peltak publish -r pypi -u PYPI_USERNAME -p PYPI_PASSWORD
