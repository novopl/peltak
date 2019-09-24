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
""" Template engine for scripts. """
from typing import Any, Dict

# 3rd party imports
import jinja2

# local imports
from peltak.core import fs
from peltak.core import shell
from peltak.core import util


class TemplateEngine(util.Singleton):
    """ Template engine wrapper.

    This class hides all jinja2 internals and exposes a simple and consistent
    API to work with templates.
    """
    def __init__(self):
        if not self._singleton_initialized:
            self.env = self._make_env()
            pass

    def render(self, template_str, template_ctx):
        # type: (str, Dict[str, Any]) -> str
        """ Render the given template. """
        return self.env.from_string(template_str).render(template_ctx)

    def _make_env(self):
        # type: () -> jinja2.Environment
        """ Initialize jinja2 env. """
        env = jinja2.Environment(
            variable_start_string='{{',
            variable_end_string='}}',
        )

        env.filters['wrap_paths'] = fs.wrap_paths
        env.filters['header'] = self.header_filter
        env.filters['count_flag'] = self.count_flag_filter

        return env

    def header_filter(self, title):
        # type: (str) -> str
        """ Converts a given title into a pretty header with colors.

        Converts a given string to:

            '= {title} =============================================='

        The resulting string will be colored for printing in the terminal.
        """
        remaining = 80 - len(title) - 3
        return shell.fmt('<32>= <35>{title} <32>{bar}<0>',
                         title=title,
                         bar='=' * remaining)

    def count_flag_filter(self, count, flag):
        # type: (int, str) -> str
        """ Returns the given flag letter as a count flag. """
        return '-' + flag * count if count else ''


# Used only in type hint comments.
del Dict, Any
