# -*- coding: utf-8 -*-
""" Types and classes used across **peltak** codebase. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any, Callable, Dict, List

# 3rd party imports
import attr

# local imports
from six import string_types


AnyFn = Callable[..., Any]
YamlConf = Dict[str, Any]
CliOptions = Dict[str, Any]


@attr.s
class FilesCollection(object):
    """ Configure files passed to the script.

    This section allows you to inject a set of files into the script as the
    ``{{ files }}`` expression. This configuration allows you to flexibly define
    what files are collected by specifying the *paths* of interest and further
    refining the list by *include* and *exclude* which act as a pattern based
    whitelist and blacklist for the paths specified in *paths*.

    On top of that you also have 2 boolean flags: *commit* will collect
    only files staged for commit and *untracked* (``True`` by default will
    include or not files untracked by git).
    """
    paths = attr.ib(type=List[str])
    include = attr.ib(type=List[str], factory=list)
    exclude = attr.ib(type=List[str], factory=list)
    only_staged = attr.ib(type=bool, default=False)
    untracked = attr.ib(type=bool, default=True)
    use_gitignore = attr.ib(type=bool, default=True)

    @classmethod
    def from_config(cls, files_conf):
        # type: (YamlConf) -> FilesCollection
        """ Load from config dict """
        paths = files_conf.get('paths')
        fields = attr.fields(cls)

        include = files_conf.get('include',
                                 fields.include.default.factory())  # type: ignore
        exclude = files_conf.get('exclude',
                                 fields.exclude.default.factory())  # type: ignore

        if not paths:
            raise ValueError("You must define the paths when using script files")

        # A string value is the same as one element array.
        paths = [paths] if isinstance(paths, string_types) else paths
        include = [include] if isinstance(include, string_types) else include
        exclude = [exclude] if isinstance(exclude, string_types) else exclude

        return cls(
            paths=paths,
            include=include,
            exclude=exclude,
            only_staged=files_conf.get('only_staged', fields.only_staged.default),
            untracked=files_conf.get('untracked', fields.untracked.default),
            use_gitignore=files_conf.get('use_gitignore',
                                         fields.use_gitignore.default),
        )

    def whitelist(self):
        # type: () -> List[str]
        """ Return a full whitelist for use with `fs.filtered_walk()` """
        from peltak.core import fs      # avoid circular dependency.
        from peltak.core import git

        if self.only_staged:
            # Only include committed files if commit only is true.
            include = [
                '*' + f for f in git.staged()
                if not self.include or fs.match_globs(f, self.include)
            ]
        else:
            include = list(self.include)

        return include

    def blacklist(self):
        # type: () -> List[str]
        """ Return a full blacklist for use with `fs.filtered_walk()` """
        from peltak.core import git

        exclude = list(self.exclude)

        # prepare
        if self.use_gitignore:
            exclude += git.ignore()

        if not self.untracked:
            exclude += git.untracked()

        return exclude
