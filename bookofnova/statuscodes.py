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


class ResultExceptions(object):
    def __init__(self, output):
        """
        Check the response codes that we get back from the API
        """
        self.output = output

    def _get_headers(self, resp):
        status_info = resp.getheaders()
        d_i = dict(status_info)
        return d_i

    def _resp_exp(self, resp, headers, authurl, jsonreq=None):
        """
        Non-20x status code responses.
        """
        if resp.status == 400 or resp.status == 503:
            self.output.critical('STATUS %s:\tIt looks like Shits Broken ==> %s'
                                 % (resp.status, jsonreq))
            return self._get_headers(resp)
        elif resp.status == 401:
            self.output.warn('STATUS %s:\tYou are not Authorized to perform'
                             ' this action. Please check Credentials ==> %s.'
                             ' Also this ERROR could have been caused by an'
                             ' expired Token.' % (resp.status, jsonreq))
            return self._get_headers(resp)
        elif resp.status == 409 or resp.status == 404:
            self.output.warn('STATUS\t%s: URI Not found, likely Gone'
                             % (resp.status))
            return self._get_headers(resp)
        elif resp.status == 413:
            d_i = self._get_headers(resp)
            self.output.critical('STATUS %s:\tThe System encountered an API'
                                 ' limitation : %s' % (resp.status, d_i))
            return d_i
        elif resp.status == 302 or resp.status == 500:
            self.output.critical('STATUS %s:\tNOVA-API REDIRECT =>'
                                 ' REQUEST: %s %s %s Make your request using a'
                                 ' different Protocol. (IE: HTTPS or HTTP)'
                                 % (resp.status, resp.reason, jsonreq, authurl))
            return self._get_headers(resp)
        elif resp.status >= 300 <= 600:
            self.output.error('STATUS %s:\tNOVA-API FAILURE =='
                              ' > REQUEST: %s %s %s'
                              % (resp.status, resp.reason, jsonreq, authurl))
            return self._get_headers(resp)
