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
""" Simple command line form/wizard implementation. """
import re
import sys
from typing import Any, Callable, Dict, Optional, Tuple

import click


IS_TTY = sys.stdout.isatty()


class Field(object):
    """ Defines a field on a form.

    Each field has a unique ID that can be used to identify it on the form.

    Attributes:
        id (str):
            Field ID. The ID will be used in the form as the key for the user
            input. This should be unique across the form.
        prompt (str):
            The text of the prompt displayed to the user. Should not include
            any styling like colors as this will be handled automatically.
        type (Callable):
            The user input type converter. This should be a callable that when
            called with the string provided by the user should return the python
            representation of the value or raise `ValueError` if user input is
            invalid.
        default (Any):
            The default value. If the form is ran in quick mode, it will be used
            instead of asking the user.
        help (str):
            Help text displayed above the prompt. This should describe what the
            value is used for so the user can better understand what's required
            of him.
    """
    _idx = 0

    def __init__(
        self,
        prompt: str,
        type: Callable,
        help: str,
        default: Optional[Any] = None
    ):
        self._idx += 1

        self.id: Optional[str] = None
        self.form = None

        self.prompt = prompt
        self.type = type
        self.help = help
        self.default = default

    def bind(self, field_id: str):
        """ Bind this field to the given ID.

        The field ID is usually the name of the field attribute as defined in
        the final form so cannot be provided in the constructor. The ID will
        be extracted from attribute name by `FormMeta` metaclass.
        """
        self.id = field_id
        return self

    @property
    def pretty_prompt(self) -> str:
        """ Return a colorized prompt ready to be displayed to the user. """
        return fmt('<1>{}<0>'.format(self.prompt))


class FormMeta(type):
    """ Form metaclass.

    It will bind all the fields in the form and make them available as
    ``cls.fields`` attribute for easy access.
    """
    def __init__(cls, name: str, bases: Tuple[type], attrs: Dict[str, Any]):
        super(FormMeta, cls).__init__(name, bases, attrs)

        cls.fields = sorted(
            (field.bind(name) for name, field in attrs.items()
             if isinstance(field, Field)),
            key=lambda x: x._idx        # noqa
        )


class Form(metaclass=FormMeta):
    """ CLI form.

    This class makes it easy to create a CLI forms/wizards when you need to
    ask the user for more details in order to continue.
    """
    def __init__(self):
        self.values: Dict[str, Any] = {}

    def run(self, quick: bool = False) -> 'Form':
        # .fields is injected by the metaclass
        for field in self.fields:   # type: ignore
            self.values[field.id] = self.get_value(field, quick)

        return self

    def __getitem__(self, item):
        return self.values[item]

    def get_value(self, field: Field, quick: bool) -> Any:
        """ Ask user the question represented by this instance.

        Args:
            field (Field):
                The field we're asking the user to provide the value for.
            quick (bool):
                Enable quick mode. In quick mode, the form will reduce the
                number of question asked by using defaults wherever possible.
                This can greatly reduce the number of interactions required on
                the user part, but will obviously limit the user choices. This
                should probably be enabled only by a specific user action
                (like passing a ``--quick`` flag etc.).

        Returns:
            The user response converted to a python type using the
            :py:attr:`cliform.core.Field.type` converter.
        """
        if callable(field.default):
            default = field.default(self)
        else:
            default = field.default

        if quick and default is not None:
            return default

        cprint('<90>{}', field.help)

        while True:
            try:
                answer = click.prompt(field.pretty_prompt, default=default)
                return field.type(answer)
            except ValueError:
                cprint("<31>Unsupported value")


def fmt(msg: str, *args: Any, **kw: Any) -> str:
    """ Generate shell color opcodes from a pretty coloring syntax. """
    global IS_TTY

    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    opcode_subst = '\x1b[\\1m' if IS_TTY else ''
    return re.sub(r'<(\d{1,2})>', opcode_subst, msg)


def cprint(msg: str, *args: Any, **kw: Any):
    """ Print colored message to stdout. """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    print(fmt('{}<0>'.format(msg)))
