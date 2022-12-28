# Copyright 2017-2020 Mateusz Klos
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
import dataclasses
from typing import Any, Callable, Dict, List, Optional, Type, cast

from peltak.cli import click, pretend_option, verbose_option
from peltak.core import types


AnyFn = Callable[..., Any]
YamlConf = Dict[str, Any]
CliOptions = Dict[str, Any]


@dataclasses.dataclass
class ScriptOption:
    """ Describes the scripts command line option. """
    name: List[str]
    default: Optional[Any] = None
    about: str = ''
    is_flag: bool = False
    count: bool = False
    type: Type = str

    @classmethod
    def from_config(cls: Type['ScriptOption'], option_conf: YamlConf) -> 'ScriptOption':
        """ Load script option from configuration in pelconf.yaml """
        fields = {f.name: f for f in dataclasses.fields(cls)}
        name = option_conf.get('name')

        if not name:
            raise ValueError("You must define the name of the option")

        if isinstance(name, str):
            # Support passing name: ['--opt'] or name: '--opt'
            name = [name]

        # Convert string type to an initializer for that type.
        if 'type' not in option_conf:
            opt_type = fields['type'].default
        else:
            opt_type = {
                'str': str,
                'int': int,
                'float': float,
            }.get(option_conf['type'])

            if not opt_type:
                raise ValueError("Unsupported {} option type {}".format(
                    name, option_conf['type']
                ))

        return cls(
            name=name,
            default=option_conf.get('default', fields['default'].default),
            about=option_conf.get('about', fields['about'].default),
            is_flag=option_conf.get('is_flag', fields['is_flag'].default),
            count=option_conf.get('count', fields['count'].default),  # type: ignore
            type=cast(Type, opt_type),
        )


@dataclasses.dataclass
class Script:
    """ Represents a single script defined in pelconf.yaml.

    The important thing is to do a little as possible during creation and only
    do heavy stuff inside the `Script.run()` method. This is because the
    scripts are parsed in a *post-conf-load* hook and that code impacts the
    speed of shell auto completion for peltak command.
    """
    name: str
    command: str
    command_file: Optional[str] = None
    about: str = ''
    root_cli: bool = False
    success_exit_codes: List[int] = dataclasses.field(default_factory=lambda: [0])
    options: List[ScriptOption] = dataclasses.field(default_factory=list)
    files: Optional[types.FilesCollection] = None
    # Script can use any (or none) of the peltak provided helpers.
    use: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_config(cls, name: str, script_conf: YamlConf) -> 'Script':
        """ Load script from pelfconf.yaml """
        fields = {f.name: f for f in dataclasses.fields(cls)}
        options = script_conf.get(
            'options',
            fields['options'].default_factory(),  # type: ignore
        )
        files = None
        success_exit_codes = script_conf.get(
            'success_exit_codes',
            fields['success_exit_codes'].default_factory(),   # type: ignore
        )

        # Parse 'files' section if it's present
        if 'files' in script_conf:
            files = types.FilesCollection.from_config(script_conf['files'])

        if isinstance(success_exit_codes, int):
            success_exit_codes = [success_exit_codes]

        # Cannot have a script without a 'command' or `command_file`.
        if 'command' not in script_conf and 'command_file' not in script_conf:
            raise ValueError(
                "'command' or 'command_file' must be specified "
                "for script '{}'".format(name)
            )

        return cls(
            name=name,
            command=script_conf.get('command', ''),
            command_file=script_conf.get('command_file', ''),
            about=script_conf.get('about', fields['about'].default),
            root_cli=script_conf.get('root_cli', fields['root_cli'].default),
            success_exit_codes=success_exit_codes,
            options=[ScriptOption.from_config(opt_conf) for opt_conf in options],
            files=files,
            use=script_conf.get('use', [])
        )

    def register(self, cli_group: Any):
        """ Register the script with click.

        *cli_group* is the result of using the ``@click.group()`` decorator.
        """
        @verbose_option
        @pretend_option
        @click.pass_context
        def script_command(ctx, **options):  # pylint: disable=missing-docstring
            from .logic import run_script  # nocov
            run_script(self, options)   # nocov

        script_command.__doc__ = self.about

        # Add all option definitions to the generated click command.
        for option in self.options:
            script_command = self._add_option(script_command, option)

        cli_group.command(self.name)(script_command)

    def _add_option(self, cmd_fn: AnyFn, option: ScriptOption) -> AnyFn:
        return click.option(
            *option.name,
            is_flag=option.is_flag,
            default=option.default,
            help=option.about,
            count=option.count,
            type=option.type
        )(cmd_fn)

    @property
    def header(self) -> Dict[str, Any]:
        result = dataclasses.asdict(self)
        del result['command']
        return result
