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
""" Application entry point. """

# Scripts should be available by default
import peltak.cli.scripts  # noqa: F401 pylint: disable=unused-import
# Make sure config is loaded
from peltak.cli import peltak_cli
from peltak.core import context  # noqa: F401 pylint: disable=unused-import
from peltak.core import conf


__all__ = [
    'peltak_cli'
]


# Accessing the config for the first time will load it.
# This is crucial for the completion to work well. We need to load the config
# here so we have autocompletion for all commands defined in the config.
conf.init()


from peltak.cli.peltak import clean  # noqa: F401, E402 pylint: disable=unused-import
