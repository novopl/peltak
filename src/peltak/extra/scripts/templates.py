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
#########################
Script template reference
#########################

.. module: peltak.extra.scripts.templates
    :synopsis: Script template reference

Template context
================

.. automodule:: peltak.extra.scripts.filters
    :members:

"""
from typing import Any, Dict

# 3rd party imports
import jinja2

# local imports
from peltak.core import fs
from peltak.core import util
from . import filters


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
        env.filters['header'] = filters.header
        env.filters['count_flag'] = filters.count_flag

        return env


# Used only in type hint comments.
del Dict, Any
