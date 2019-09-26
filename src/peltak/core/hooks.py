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
"""

###########
Using Hooks
###########

Hook allow responding to various events during command execution. Peltak exposes
a set of standard hooks that you can use to react to what's happening. Commands
(including ones in external packages) can provide their own hooks to be used
by other commands.

To call a hook you don't have to register it, just know it's name. You can do
it simply with:

.. code-block:: python

    from peltak.commands import root_cli
    from peltak.core import hooks

    @root_cli.command('test-command')
    def test_command():
        hooks.call('pre-test-command', 3.14159, msg='hello, world!')


Registering a handler for any hook is also very simple:

.. code-block:: python

    from peltak.core import hooks

    @hooks.register('pre-test-command')
    def pre_test_command(pi, msg='<msg missing>'):
        print("pre_test_command called with ({}, {})".format(pi, msg))

"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from types import FunctionType
from typing import Any, Callable


AnyFunc = Callable[..., Any]
Decorator = Callable[[AnyFunc], AnyFunc]


class HooksRegister(object):
    """ Intermediary between hooks emitters and handlers. """
    def __init__(self):
        self.hooks = {}

    def remove(self, name, fn):
        # type: (str, AnyFunc) -> None
        """ Remove a handler for a given hook.

        After this call, the *fn* function won't be called when the hook is
        called.

        Args:
            name:
                The name of the hook.
            fn:
                The function that we want to unregister from the hook calls.
        """
        handlers = self.hooks.get(name, [])
        handlers.remove(fn)

    def call(self, name, *args, **kw):
        # type: (str, *Any, **Any) -> None
        """ Call all hooks registered for the given name.

        This will pass all arguments except for the name directly to the hook.
        Remember that hook handler should not modify those arguments as that
        will affect all hooks called later in the sequence.

        Args:
            name:
                Then name of the hook.
            *args, \**kw:
                Arguments and keyword arguments that should be passed to the
                hook handlers.
        """
        if not name:
            raise ValueError("name cannot be empty")

        handlers = self.hooks.get(name, [])
        for handler_fn in handlers:
            handler_fn(*args, **kw)

    def __call__(self, name):
        # type: (str) -> Decorator
        """ Return a decorator that will register the wrapped function under name.

        Args:
            name (str):
                The name of the hook you are subscribing to.
        """
        if not name:
            raise ValueError("name cannot be empty")

        def decorator(fn):      # pylint: disable=missing-docstring
            # type: (AnyFunc) -> AnyFunc
            self._register_handler(name, fn)
            return fn
        return decorator

    def _register_handler(self, name, fn):
        # type: (str, AnyFunc) -> None
        handlers = self.hooks.setdefault(name, [])

        if fn in handlers:
            raise ValueError("{} already registered for {}", fn, name)

        handlers.append(fn)


register = HooksRegister()


# Used only in type hint comments.
del Any, Callable, FunctionType, Decorator      # type: ignore
