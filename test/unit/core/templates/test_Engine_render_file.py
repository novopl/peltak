# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest.mock import Mock

from peltak.core import templates


def test_uses_env_get_template():
    """
    When calling Engine.render_template()
    then Engine.env.get_template is called to load the template.
    """
    # Setup
    engine = templates.Engine()
    engine.env.get_template = Mock()

    templates.Engine().render_file('fake.jinja2')

    engine.env.get_template.assert_called_once_with('fake.jinja2')


def test_passes_template_context_to_render_method():
    engine = templates.Engine()
    p_template = Mock()
    engine.env.get_template = Mock(return_value=p_template)

    templates.Engine().render_file('fake.jinja2', {'fake': 'context'})

    p_template.render.assert_called_once_with({'fake': 'context'})
