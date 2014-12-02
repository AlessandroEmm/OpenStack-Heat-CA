# Copyright 2013 Gridcentric Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
from distutils.core import setup

VERSION = os.environ.get("VERSION", '0.1')
PACKAGE = os.environ.get("PACKAGE", None)

if not(PACKAGE) or PACKAGE == "ca-heat":
    setup(name='ca-heat',
          version=VERSION,
          description='Certificate Authority resource plugin for OpenStack Heat',
          author='Alessandro Meyer',
          author_email='alessandro.meyer gmail.com',
          packages=['ca_heat'])
