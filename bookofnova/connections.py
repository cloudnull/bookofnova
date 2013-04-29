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
import json

from bookofnova import statuscodes


class Connections(object):
    def __init__(self, m_args, output):
        """
        Open, Prep, or Close a connection to the OpenStack API
        """
        self.output = output
        self.m_args = m_args
        self.resp_exp = statuscodes.ResultExceptions(self.output)

    def _conn(self, url):
        """
        Setup a connection to the OpenStack API. This allows for both HTTP and
        HTTPS to be used. By default HTTP will be used unless YOU set the
        protocol to https, this is done with by setting the
        "m_args['use_https']" argument to "True"
        """
        if not self.m_args['use_https']:
            self.conn = httplib.HTTPConnection(url)
        else:
            self.conn = httplib.HTTPSConnection(url)

        if self.m_args['os_verbose']:
            self.conn.set_debuglevel(1)
        return self.conn

    def _conn_prep(self, path, endpoint_uri):
        """
        Setup a connection for the "path" provided to it. Using this method will
        set the default headers as well as use the "endpoint_url" method.
        """
        headers = {'X-Auth-Token': self.m_args['token'],
                   'Content-type': 'application/json'}
        endpoint = endpoint_uri.strip('http?s://')
        url_data = endpoint.split('/')
        url = url_data[0]
        c_path = '/%s%s' % ('/'.join(url_data[1:]), path)
        self.output.info('Connecting to the API for %s' % path)
        self.conn = self._conn(url)
        if self.m_args['os_verbose']:
            self.output.debug('%s %s\n' % (headers, c_path))
        return c_path, headers, url, self.conn

    def check_status(self, resp, headers, authurl, jsonreq=None):
        """
        Check the status of the response that we get from the API. Note
        that the response is given to the response exception handler if the
        response if anything over 300. This also will overwrite the
        "status['nova_reason']" key with the data provided by the response
        status interperater. Also Note that the "status['nova_reason']" key
        will be set to a Tuple containing the headers if the response status is
        above 300
        """
        # Status Data
        self.m_args['nova_status'] = resp.status
        self.m_args['nova_reason'] = resp.reason
        if resp.status >= 300:
            data = self.resp_exp._resp_exp(resp=resp,
                                           headers=headers,
                                           authurl=authurl,
                                           jsonreq=jsonreq)
            self.m_args['nova_resp'] = data

    def _delete_action(self, path, args):
        """
        Delete Request.
        """
        _cp = self._conn_prep(path,
                              endpoint_uri=args['nova_endpoint'])
        path, headers, url, conn = _cp

        conn.request('DELETE', path, headers=headers)
        resp = conn.getresponse()

        # Status Data
        self.check_status(resp=resp,
                          headers=headers,
                          authurl=url,
                          jsonreq=None)
        if args['nova_status'] >= 300:
            conn.close()
            return args

        read_resp = resp.read()
        conn.close()
        args['nova_resp'] = read_resp
        return args

    def _get_action(self, path, args):
        """
        Get Request
        """
        _cp = self._conn_prep(path,
                              endpoint_uri=args['nova_endpoint'])
        path, headers, url, conn = _cp

        conn.request('GET', path, headers=headers)
        resp = conn.getresponse()

        # Status Data
        self.check_status(resp=resp,
                          headers=headers,
                          authurl=url,
                          jsonreq=None)
        if args['nova_status'] >= 300:
            conn.close()
            return args
        else:
            read_resp = resp.read()
            conn.close()
            if read_resp:
                json_response = json.loads(read_resp)
            else:
                json_response = read_resp
            args['nova_resp'] = json_response
            return args

    def _post_action(self, path, args, body):
        """
        Post Request
        """
        _cp = self._conn_prep(path,
                              endpoint_uri=args['nova_endpoint'])
        path, headers, url, conn = _cp

        conn.request('POST', path, body, headers=headers)
        resp = conn.getresponse()

        # Status Data
        self.check_status(resp=resp,
                          headers=headers,
                          authurl=url,
                          jsonreq=body)
        if args['nova_status'] >= 300:
            conn.close()
            return args

        read_resp = resp.read()
        conn.close()
        if read_resp:
            json_response = json.loads(read_resp)
        else:
            json_response = read_resp

        if args['os_verbose']:
            self.output.debug(json.dumps(json_response, indent=2))
        args['nova_resp'] = json_response
        return args
