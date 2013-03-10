#!/usr/bin/env python
# ==============================================================================
# Copyright [2013] [Kevin Carter]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import setuptools
import sys
import os

if sys.version_info <= (2, 6, 0):
    sys.stderr.write("BookOfNova Presently requires Python"
                     " 2.6.0 or greater\n")
    sys.exit('Upgrade your version of python because it is VERY deprecated\n')

with open('README') as r_file:
    long_description = r_file.read()

setuptools.setup(
    name='bookofnova',
    version='0.002',
    author='Kevin Carter',
    author_email='kevin.carter@rackspace.com',
    description='Nova Action Library for Openstack Compute',
    long_description=long_description,
    license='Apache2.0',
    packages=['bookofnova'],
    url='https://github.com/cloudnull/bookofnova.git',
    classifiers=[
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )
