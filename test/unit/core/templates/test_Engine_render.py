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
    engine.env.from_string = Mock()

    templates.Engine().render('fake template string')

    engine.env.from_string.assert_called_once_with('fake template string')


def test_passes_template_context_to_render_method():
    engine = templates.Engine()
    p_template = Mock()
    engine.env.from_string = Mock(return_value=p_template)

    templates.Engine().render('fake template string', {'fake': 'context'})

    p_template.render.assert_called_once_with({'fake': 'context'})
