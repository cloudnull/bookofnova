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
from bookofnova import connections, statuscodes


class Authentication(object):
    def __init__(self, m_args, output):
        self.m_args = m_args
        self.output = output
        self.result_exception = statuscodes.ResultExceptions(output)

    def auth_set(self):
        """
        Set the authentication URL and STRING in JSON
        Looks for "os_arx_auth" in m_args. if RAX Auth is not set then the
        application will attempt to create an AUTH string based on the
        "os_region" and "os_auth_url"
        """
        if self.m_args['os_rax_auth'] == 'LON':
            self.m_args['os_region'] = self.m_args['os_rax_auth']
            self.m_args['os_auth_url'] = 'lon.identity.api.rackspacecloud.com'

        elif (self.m_args['os_rax_auth'] == 'DFW' or
              self.m_args['os_rax_auth'] == 'ORD'):
            self.m_args['os_region'] = self.m_args['os_rax_auth']
            self.m_args['os_auth_url'] = 'identity.api.rackspacecloud.com'

        else:
            if not self.m_args['os_region']:
                self.output('FAIL\t: You have to specify'
                                 ' a Region along with an Auth URL')
            elif not self.m_args['os_auth_url']:
                self.output('FAIL\t: You have to specify an Auth URL'
                                     ' along with the Region')

        if 'os_rax_auth' in self.m_args:
            if self.m_args['os_rax_auth']:
                self.m_args['rackspace_auth'] = True
                self.m_args['use_https'] = True

        if self.m_args['os_apikey'] and self.m_args['os_rax_auth']:
            jsonreq = json.dumps({'auth':
                {'RAX-KSKEY:apiKeyCredentials':
                    {'username': self.m_args['os_user'],
                     'apiKey': self.m_args['os_apikey']
                     }}})
        else:
            jsonreq = json.dumps({'auth':
                {"tenantName": self.m_args['os_tenant'],
                 'passwordCredentials': {'username': self.m_args['os_user'],
                                         'password': self.m_args['os_password']
                                         }}})
        if self.m_args['os_auth_url'].startswith('https'):
            self.m_args['use_https'] = True

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
        self.output(self.m_args)
        self.connection = connections.Connections(m_args=self.m_args,
                                                  output=self.output)
        conn = self.connection._conn(self.m_args['url'])

        if self.m_args['os_verbose']:
            self.output('%s\n' % self.m_args)
            self.output('REQUEST\t: %s\n' % jsonreq)

        headers = {'Content-Type': 'application/json'}
        tokenurl = '/%s/tokens' % self.m_args['os_version']
        conn.request('POST', tokenurl, jsonreq, headers)

        try:
            resp = conn.getresponse()
        except httplib.BadStatusLine, exp:
            self.output(exp)
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
            self.parse_auth(json_response=json_response,
                            resp=resp)
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
            # loop through the Service Catalog
            for service in json_response['access']['serviceCatalog']:
                if service['name'].upper() == 'CLOUDSERVERSOPENSTACK':
                    for endpoint in service['endpoints']:
                        if endpoint['region'] == self.m_args['os_region']:
                            rax_cs = endpoint['publicURL']
                            self.m_args['nova_endpoint'] = rax_cs

                if service['name'].upper() == 'NOVA':
                    for endpoint in service['endpoints']:
                        if endpoint['region'] == self.m_args['os_region']:
                            os_nova = endpoint['publicURL']
                            self.m_args['nova_endpoint'] = os_nova

            # Set the token and Tenant ID
            tenant_id = json_response['access']['token']['tenant']['id']
            self.m_args['tenantid'] = tenant_id
            self.m_args['token'] = json_response['access']['token']['id']
        except (Exception, UserWarning):
            self.output('Shits Borke Son...')
            self.output(traceback.format_exc())

        # If this is a Rackspace Account set the Rackspace_auth flag
        if 'rackspace_auth' in self.m_args:
            if not self.m_args['rackspace_auth']:
                for ident in json_response['access']['user'].keys():
                    if ident.startswith('RAX-AUTH') is True:
                        self.m_args['rackspace_auth'] = True
                    else:
                        self.m_args['rackspace_auth'] = False

        if self.m_args['os_verbose']:
            self.output(json.dumps(json_response, indent=2))
            self.output(self.m_args)
