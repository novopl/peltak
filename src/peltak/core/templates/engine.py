# -*- coding: utf-8 -*-
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
""" Engine wraps the jinja2 environment and exposes it to the rest of the code. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any, Dict

# 3rd party imports
import jinja2

# local imports
from peltak.core import util
from . import filters


class Engine(util.Singleton):
    """ Template engine wrapper.

    Engine is a singleton, which means there is always a single instance
    in existence during the app run. You can access this instance by calling
    the class initializer:

    >>> from peltak.core.templates import Engine
    >>>
    >>> engine = Engine()


    Only on first call will the class be actually constructed, all following
    calls will return the same instance:

    >>> from peltak.core.templates import Engine
    >>>
    >>> Engine() is Engine()
    True

    """
    def __init__(self):
        if not self._singleton_initialized:
            self.env = self._make_env()
            pass

    def render(self, template_str, template_ctx=None):
        # type: (str, Dict[str, Any]) -> str
        """ Render a script template using the given context.

        Examples:

            >>> from peltak.core.templates import Engine
            >>>
            >>> Engine().render("{{ msg | upper }}", {'msg': 'hello'})
            'HELLO'

        """
        return self.env.from_string(template_str).render(template_ctx)

    def render_file(self, template_file, template_ctx=None):
        # type: (str, Dict[str, Any]) -> str
        """ Render a template file from src/peltak/templates directory.

        All built-in peltak templates should go to the ``src/peltak/templates``
        directory.

        Args:
            template_file (str):
                The name of the template file to use. This file needs to reside
                in the templates directory and will be automatically loaded.
            template_ctx (dict[str, Any]):
                The template context to use. This is a dictionary of values that
                will be injected into the template during rendering.

        Returns:
            str: A rendered template.

        Examples:

            \b
            >>> from peltak.core.templates import Engine
            >>>
            >>> Engine().render_file("pelconf.yaml", {'src_dir': 'src'})
            # peltak configuration file
            # Visit https://novopl.github.io/peltak for more information
            pelconf_version: '1'
            # You can add custom project commands or 3rd party packages here.
            commands:
              - peltak.extra.git
              - peltak.extra.gitflow
              - peltak.extra.scripts

            # This directory will be added to sys.path when the config is loaded.
            # Useful if do not keep the source code in th root directory.
            src_dir: "src"

            # Scripts to help you manage your project.
            scripts:
              test:
                about: Test your code
                command: |
                  echo "Change me, to run your tests"

        """
        template = self.env.get_template(template_file)
        return template.render(template_ctx)

    def _make_env(self):
        # type: () -> jinja2.Environment
        """ Initialize jinja2 env. """
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('peltak', 'templates'),
            variable_start_string='{{',
            variable_end_string='}}',
        )

        env.filters['header'] = filters.header
        env.filters['count_flag'] = filters.count_flag
        env.filters['cprint'] = filters.cprint
        env.filters['wrap_paths'] = filters.wrap_paths

        return env


# Used only in type hint comments.
del Dict, Any
