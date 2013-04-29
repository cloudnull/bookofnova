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
import httplib
import traceback
import json

# Local Import
from bookofnova import connections, statuscodes, logger


class NoEndPointProvided(Exception):
    pass


class NoAuthURLProvided(Exception):
    pass


class Authentication(object):
    def __init__(self, m_args, output):
        """
        Perform Nova Authentication
        """
        self.m_args = m_args
        self.output = output
        self.result_exception = statuscodes.ResultExceptions(self.output)

    def auth_set(self):
        """
        Set the authentication URL and STRING in JSON
        Looks for "os_rax_auth" in m_args. if RAX Auth is not set then the
        application will attempt to create an AUTH string based on the
        "os_region" and "os_auth_url which is the proper Openstack way to do it.
        Also This section does error checking on the provided information and
        attmpts to create the best string possible for the endpoint we will be
        Authenticating against."
        """
        # Look for Known RAX Endpoints
        known_rax = {'LON': 'lon.identity.api.rackspacecloud.com',
                     'DFW': 'identity.api.rackspacecloud.com',
                     'ORD': 'identity.api.rackspacecloud.com'}
        if ('os_password' in self.m_args and
            self.m_args['os_password']):
            self.m_args['os_apikey'] = self.m_args['os_password']
        else:
            self.m_args['os_password'] = self.m_args['os_apikey']

        if ('os_rax_auth' in self.m_args and
            self.m_args['os_rax_auth']):
            id_name = self.m_args['os_rax_auth'].upper()
            if id_name in known_rax:
                self.m_args['os_auth_url'] = known_rax[id_name]
                self.m_args['rackspace_auth'] = True
                self.m_args['use_https'] = True
                self.m_args['os_region'] = id_name
            else:
                raise NoEndPointProvided('To use "os_rax_auth" you have to use'
                                         ' one of the known Data Centers, here'
                                         ' are your choices. "%s"'
                                         % known_rax)

        elif ('os_auth_url' in self.m_args and
              self.m_args['os_auth_url']):
            # Look at the URL For RAX Endpoints
            temp_url = self.m_args['os_auth_url']
            temp_url = temp_url.strip('http?s://').split('/')
            temp_url = temp_url[0]
            if temp_url.endswith('rackspacecloud.com'):
                self.m_args['rackspace_auth'] = True
                self.m_args['use_https'] = True
            else:
                self.m_args['rackspace_auth'] = False

            # Check to see if we are using HTTPS
            if self.m_args['os_auth_url'].startswith('https'):
                self.m_args['use_https'] = True
            else:
                self.m_args['use_https'] = False

        else:
            # Make sure you provided a region and endpoint
            if not self.m_args['os_region']:
                raise NoEndPointProvided('FAIL\t: You have to specify'
                                         ' a Region along with an Auth URL')
            elif not self.m_args['os_auth_url']:
                raise NoAuthURLProvided('FAIL\t: You have to specify an Auth'
                                        ' URL along with the Region')
            if not 'use_https' in self.m_args:
                self.m_args['use_https'] = False

        if ('rackspace_auth' in self.m_args and
            self.m_args['rackspace_auth']):
            jsonreq = json.dumps({'auth': {'RAX-KSKEY:apiKeyCredentials':
                {'username': self.m_args['os_user'],
                 'apiKey': self.m_args['os_apikey']
                 }}})
        else:
            if not 'os_tenant' in self.m_args or not self.m_args['os_tenant']:
                self.m_args['os_tenant'] = self.m_args['os_user']
            jsonreq = json.dumps({'auth':
                {"tenantName": self.m_args['os_tenant'],
                 'passwordCredentials': {'username': self.m_args['os_user'],
                                         'password': self.m_args['os_password']
                                         }}})

        # Sanitise the URL
        strip_url = self.m_args['os_auth_url'].strip('http?s://')
        self.m_args['os_auth_url'] = strip_url
        url_data = self.m_args['os_auth_url'].split('/')
        self.m_args['url'] = url_data[0]
        return self.m_args, jsonreq

    def os_auth(self):
        """
        Set a DC Endpoint and Authentication URL for the Open Stack environment
        Authentication can handle both HTTPS and HTTP Connections.
        """
        # Set Auth Sting and URL
        data = self.auth_set()
        self.m_args = data[0]
        jsonreq = data[1]
        self.connection = connections.Connections(m_args=self.m_args,
                                                  output=self.output)
        conn = self.connection._conn(self.m_args['url'])

        if self.m_args['os_verbose']:
            self.output.debug('REQUEST:\t %s\nARGS:\t%s'
                              % (jsonreq, self.m_args))

        headers = {'Content-Type': 'application/json'}
        tokenurl = '/%s/tokens' % self.m_args['os_version']
        conn.request('POST', tokenurl, jsonreq, headers)

        try:
            resp = conn.getresponse()
        except httplib.BadStatusLine, exp:
            self.output.error(exp)
            return False

        # Set the status Codes
        self.m_args['nova_status'] = resp.status
        self.m_args['nova_reason'] = resp.reason
        if resp.status >= 300:
            data = self.result_exception._resp_exp(resp=resp,
                                           headers=headers,
                                           authurl=self.m_args['os_auth_url'],
                                           jsonreq=jsonreq)
            self.m_args['nova_reason'] = data
            return self.m_args
        else:
            readresp = resp.read()
            conn.close()
            json_response = json.loads(readresp)
            self.output.debug(readresp)
            self.parse_auth(json_response=json_response,
                            resp=resp)
            self.m_args['nova_resp'] = json_response
            return self.m_args

    def parse_auth(self, json_response, resp):
        """
        Parse the arguments post authentication This will set the credentials
        including the token into the main dictionary. This loads Endpoints.
        To extend this module to set more enpoints simply follow the loop
        method. The serviceCatalog is used as a dictionary and everything in the
        service catalog is parsed as Key=Value. Notice that in my loops, I use
        ".upper()" which is not required, just allows the instances names to be
        uniform as I loop through them.
        """
        try:
            # List of Known Regions
            known_services = ['CLOUDSERVERSOPENSTACK',
                              'NOVA']

            # loop through the Service Catalog
            for service in json_response['access']['serviceCatalog']:
                if service['name'].upper() in known_services:
                    for endpoint in service['endpoints']:
                        user_region = self.m_args['os_region'].upper()
                        cata_region = endpoint['region'].upper()
                        if cata_region == user_region:
                            r_cs = endpoint['publicURL']
                            self.m_args['nova_endpoint'] = r_cs

            if not 'nova_endpoint' in self.m_args:
                ep_d = json_response['access']['serviceCatalog']
                ep_data = []
                for _ep in ep_d:
                    ep_data.append(_ep['name'])
                raise NoEndPointProvided('Authentication was OK, though we'
                                         ' were not able to find an'
                                         ' application to use in our Nova'
                                         ' ComputeLib. Use Debug to see what is'
                                         ' in your service catalog. Here are'
                                         ' your available Services "%s"'
                                         % ep_data)

            # Set the token and Tenant ID
            tenant_id = json_response['access']['token']['tenant']['id']
            self.m_args['tenantid'] = tenant_id
            self.m_args['token'] = json_response['access']['token']['id']
        except (Exception, UserWarning):
            self.output.error(traceback.format_exc())

        # If this is a Rackspace Account set the Rackspace_auth flag
        if 'rackspace_auth' in self.m_args:
            if not self.m_args['rackspace_auth']:
                for ident in json_response['access']['user'].keys():
                    if ident.startswith('RAX-AUTH') is True:
                        self.m_args['rackspace_auth'] = True
                    else:
                        self.m_args['rackspace_auth'] = False

        if self.m_args['os_verbose']:
            self.output.debug(json.dumps(json_response))
