Book Of Nova
############
:date: 2012-03-08 16:22
:tags: Openstack, Nova Compute, Nova
:category: \*nix


Access Openstack Nova Compute via Python
========================================

General Overview
----------------

This is a VERY Simple library which I have found useful in projects where I needed access to the Openstack NOVA Compute API and I did not want to bother with novaclient.


Functions of the Library :
  * Do Openstack Nova Things
  * Presently only supports Openstack Nova Compute, but does so for both Vanilla Openstack and the Rackspace Open Cloud
  * Not all of the functions are built-in however the library is extendable and I would be happy to add things in as needed / requested. 


Prerequisites :
  * Python => 2.6 but < 3.0


Installation is simple :

    .. code-block:: bash

        git clone git://github.com/cloudnull/bookofnova.git
        cd bookofnova
        python setup.py install


Now in your application *Import bookofnova* and go forth and Access Openstack Nova.


Application Usage
-----------------

Here is some Basic Usage :


    .. code-block:: python

        # Everything in this dictionary is a string, fill in the needed values.
        m_args = {"os_user": 'YOURUSERNAME',
                  "os_apikey": 'RANDOMNUMBERSANDTHINGS',
                  "os_auth_url": None,
                  "os_rax_auth": 'ALOCATION',
                  "os_verbose": None,
                  "os_password": None,
                  "os_tenant": None,
                  "os_region": None,
                  "os_version": 'v2.0'}


    .. code-block:: python

        # The "__future__" import is not required, but its nice for the example
        from __future__ import print_function
        from bookofnova import authentication, computelib, connections
        
        # Set output / Logging
        output = print
        
        # Authentication with Nova
        auth = authentication.Authentication(m_args=m_args,
                                             output=output)
        service_cat = auth.os_auth()
        
        # Tell the book of Nova that you are ready
        nova = computelib.NovaCommands(m_args=m_args,
                                       output=output)
        
        # Using Nova to show a list of all Instances
        servers = nova.server_list()
        print(servers)
        
        # now everything that you ever wanted to know from a Openstack Nova
        # query can be found in your dictionary under the key 'nova_resp'


Get Social
----------

* Downloadable on PyPi_
* Downloadable on GitHub_
* See My `GitHub Issues Page`_ for any and all Issues or Feature requests

.. _PyPi: https://pypi.python.org/pypi/bookofnova
.. _GitHub: https://github.com/cloudnull/bookofnova
.. _GitHub Issues Page: https://github.com/cloudnull/bookofnova/issues

See ``https://github.com/cloudnull/bookofnova/issues`` for Issues or Feature requests


License
_______

Copyright [2013] [Kevin Carter]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.