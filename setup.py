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

if sys.version_info < (2, 6, 0):
    sys.stderr.write("NovaLib Presently requires Python"
                     " 2.6.0 or greater\n")
    sys.exit('Upgrade python because you version of it is VERY deprecated\n')

user = os.getuid()
if user != 0:
    sys.exit('This program requires root privileges.'
             ' Run as root, or use "sudo"')

#with open('README') as file:
#    long_description = 'Things and Stuff, More coming...'

long_description = 'Things and Stuff, More coming...'

setuptools.setup(
    name='bookofnova',
    version='0.001',
    author='Kevin Carter',
    author_email='kevin.carter@rackspace.com',
    description='Nova Action Library for Compute',
    long_description='Here is a long description, More coming...',
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
