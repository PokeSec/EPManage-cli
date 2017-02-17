"""
api.py : EPManage APIs

This file is part of EPControl.

Copyright (C) 2016  Jean-Baptiste Galet & Timothe Aeberhardt

EPControl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

EPControl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with EPControl.  If not, see <http://www.gnu.org/licenses/>.
"""
import requests.auth

from epmanage import __version__


class EPCAuth(requests.auth.AuthBase):
    """Custom authentication class. Currently uses JWT"""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers.update({
            'Authorization': 'Bearer {}'.format(self.token),
            'User-Agent': 'EPControl/{}'.format(__version__)
        })
        return r


class EPSession(requests.Session):
    """Custom session to provide dynamic routing"""

    def __init__(self):
        super().__init__()
        self.base_url = ''

    def prepare_request(self, request):
        """
        Modify the request before sending it:
        * Get the appropriate URL during request preparation
        """
        if not request.url.startswith('http'):
            request.url = self.base_url + request.url

        return super().prepare_request(request)

    def request(self, method, url,
                params=None,
                data=None,
                headers=None,
                cookies=None,
                files=None,
                auth=None,
                timeout=None,
                allow_redirects=True,
                proxies=None,
                hooks=None,
                stream=None,
                verify=None,
                cert=None,
                json=None):
        """
        Prepare the request before sending it:
        * Refuse any communication if base_url is not set
        """
        if not self.base_url:
            raise CommException("No base_url...refusing communication")

        return super(EPSession, self).request(
            method,
            url,
            params,
            data,
            headers,
            cookies,
            files,
            auth,
            timeout,
            allow_redirects,
            proxies,
            hooks,
            stream,
            verify,
            cert,
            json)

req_sess = EPSession()
CommException = requests.exceptions.RequestException


def setup_auth(token):
    """Setup the authentication module"""
    req_sess.auth = EPCAuth(token)
