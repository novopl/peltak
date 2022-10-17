""" Types and classes used across **peltak** codebase. """
import dataclasses
from typing import Any, Callable, Dict, List, Type, Union


AnyFn = Callable[..., Any]
YamlConf = Dict[str, Any]
CliOptions = Dict[str, Any]
PlainDict = Dict[str, Any]
JsonDict = Union[PlainDict, List[Any]]
Decorator = Callable[[AnyFn], AnyFn]


@dataclasses.dataclass
class FilesCollection:
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
    paths: List[str]
    include: List[str] = dataclasses.field(default_factory=list)
    exclude: List[str] = dataclasses.field(default_factory=list)
    only_staged: bool = False
    untracked: bool = True
    use_gitignore: bool = True

    @classmethod
    def from_config(
        cls: Type['FilesCollection'],
        files_conf: YamlConf,
    ) -> 'FilesCollection':
        """ Load from config dict """
        paths = files_conf.get('paths')
        fields = {f.name: f for f in dataclasses.fields(cls)}
        include = files_conf.get(
            'include',
            fields['include'].default_factory()  # type: ignore
        )
        exclude = files_conf.get(
            'exclude',
            fields['exclude'].default_factory()  # type: ignore
        )

        if not paths:
            raise ValueError("You must define the paths when using script files")

        # A string value is the same as one element array.
        paths = [paths] if isinstance(paths, str) else paths
        include = [include] if isinstance(include, str) else include
        exclude = [exclude] if isinstance(exclude, str) else exclude

        return cls(
            paths=paths,
            include=include,
            exclude=exclude,
            only_staged=files_conf.get('only_staged', fields['only_staged'].default),
            untracked=files_conf.get('untracked', fields['untracked'].default),
            use_gitignore=files_conf.get(
                'use_gitignore', fields['use_gitignore'].default,
            ),
        )

    def whitelist(self) -> List[str]:
        """ Return a full whitelist for use with `fs.filtered_walk()` """
        from peltak.core import fs  # avoid circular dependency.
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

    def blacklist(self) -> List[str]:
        """ Return a full blacklist for use with `fs.filtered_walk()` """
        from peltak.core import git

        exclude = list(self.exclude)

        # prepare
        if self.use_gitignore:
            exclude += git.ignore()

        if not self.untracked:
            exclude += git.untracked()

        return exclude
