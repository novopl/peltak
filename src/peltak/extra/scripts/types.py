# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" Types and classes used by ``peltak.extra.scripts``. """

# stdlib imports
from typing import Any, Dict, List

# 3rd party imports
import attr

# local imports
from six import string_types
from peltak.commands import click, pretend_option, verbose_option


YamlConf = Dict[str, Any]
CliOptions = Dict[str, Any]


@attr.s
class ScriptOption(object):
    """ Describes the scripts command line option. """
    name = attr.ib(type=List[str])
    default = attr.ib(type=Any, default=None)
    about = attr.ib(type=str, default='')
    is_flag = attr.ib(type=bool, default=False)

    @classmethod
    def from_config(cls, option_conf):
        # type: (YamlConf) -> ScriptOption
        """ Load script option from configuration in pelconf.yaml """
        fields = attr.fields(cls)
        name = option_conf.get('name')

        if not name:
            raise ValueError("You must define the name of the option")

        if isinstance(name, string_types):
            # Support passing name: ['--opt'] or name: '--opt'
            name = [name]

        return cls(
            name=name,
            default=option_conf.get('default', fields.default.default),
            about=option_conf.get('about', fields.about.default),
            is_flag=option_conf.get('is_flag', fields.is_flag.default)
        )


@attr.s
class ScriptFiles(object):
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
    paths = attr.ib(type=bool)
    include = attr.ib(type=List[str], factory=list)
    exclude = attr.ib(type=List[str], factory=list)
    commit = attr.ib(type=bool, default=False)
    untracked = attr.ib(type=bool, default=True)
    use_gitignore = attr.ib(type=bool, default=True)

    @classmethod
    def from_config(cls, files_conf):
        # type: (YamlConf) -> ScriptFiles
        """ Load the script files config from `pelconf.yaml` """
        paths = files_conf.get('paths')
        fields = attr.fields(cls)
        include = files_conf.get('include', fields.include.default.factory())
        exclude = files_conf.get('exclude', fields.exclude.default.factory())

        if not paths:
            raise ValueError("You must define the name of the option")

        # A string value is the same as one element array.
        paths = [paths] if isinstance(paths, string_types) else paths
        include = [include] if isinstance(include, string_types) else include
        exclude = [exclude] if isinstance(exclude, string_types) else exclude

        return cls(
            paths=paths,
            include=include,
            exclude=exclude,
            commit=files_conf.get('commit', fields.commit.default),
            untracked=files_conf.get('untracked', fields.untracked.default),
            use_gitignore=files_conf.get('use_gitignore',
                                         fields.use_gitignore.default),
        )

    def whitelist(self):
        # type: () -> List[str]
        """ Return a full whitelist for use with `fs.filtered_walk()` """
        from peltak.core import git

        include = list(self.include)

        if self.commit:
            include += ['*' + f for f in git.staged()]

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


@attr.s
class Script(object):
    """ Represents a single script defined in pelconf.yaml.

    The important thing is to do a little as possible during creation and only
    do heavy stuff inside the `Script.run()` method. This is because the
    scripts are parsed in a *post-conf-load* hook and that code impacts the
    speed of shell auto completion for peltak command.
    """
    name = attr.ib(type=str)
    command = attr.ib(type=str)
    about = attr.ib(type=str, default='')
    accept_files = attr.ib(type=str, default=False)
    success_exit_codes = attr.ib(type=List[int], factory=lambda: [0])
    options = attr.ib(type=List[ScriptOption], factory=list)
    files = attr.ib(type=ScriptFiles, default=None)

    @classmethod
    def from_config(cls, name, script_conf):
        # type: (str, YamlConf) -> Script
        """ Load script from pelfconf.yaml """
        fields = attr.fields(cls)
        options = script_conf.get('options', fields.options.default.factory())
        files = None
        success_exit_codes = script_conf.get(
            'success_exit_codes',
            fields.success_exit_codes.default.factory()
        )

        if 'files' in script_conf:
            files = ScriptFiles.from_config(script_conf['files'])

        if isinstance(success_exit_codes, int):
            success_exit_codes = [success_exit_codes]

        if 'command' not in script_conf:
            raise ValueError("Missing 'command' for '{}' script".format(name))

        return cls(
            name=name,
            command=script_conf['command'],
            about=script_conf.get('about', fields.about.default),
            accept_files=script_conf.get('accept_files', fields.about.default),
            success_exit_codes=success_exit_codes,
            options=[ScriptOption.from_config(opt_conf) for opt_conf in options],
            files=files,
        )

    def register(self, cli_group):
        # type: (click.Group) -> None
        """ Register the script with click. """
        @pretend_option
        @verbose_option
        @click.pass_context
        def script_command(ctx, **options):  # pylint: disable=missing-docstring
            from .logic import run_script
            run_script(self, options)

        script_command.__doc__ = self.about

        cli_group.command(self.name)(script_command)