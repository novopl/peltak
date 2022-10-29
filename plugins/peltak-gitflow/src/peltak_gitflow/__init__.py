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
"""
##################################
**git-flow** made easy with peltak
##################################

The improvement over raw git-flow is that you will have to type way less. Most
of the time all the branch names required will be filled in.


Default configuration
====================

.. code-block:: yaml

    version_file: '/must/be/defined/in/the/project'
    git:
        devel_branch:  'develop'
        master_branch: 'master'

"""
from .commands.feature import feature_cli  # noqa: F401
from .commands.hotfix import hotfix_cli  # noqa: F401
from .commands.release import release_cli  # noqa: F401


__version__ = '0.0.4'
