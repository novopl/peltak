# Copyright 2021 Mateusz Klos
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
###################
peltak TODOs plugin
###################


Overview
========

This plugin allows you to quickly scan your files for TODO comments and track
them across commits. This makes it easy to leave yourself todos while working on
a branch and then resolve them either before commiting or before finishing the PR.

"""
from .cli import todos  # noqa: F401


__version__ = '0.0.6'
