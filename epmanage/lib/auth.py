"""
auth.py : Authentication APIs

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
from typing import Optional, Tuple

import jwt

from epmanage.lib.api import req_sess

__token = None


def auth(email: str, password: str) -> Tuple[bool, str]:
    global __token
    req = req_sess.post(
        '/frontend/login',
        json=dict(email=email, password=password))
    if req.status_code != 200:
        return False, req.json().get('_error', dict()).get('message', 'Unknown error')
    else:
        __token = req.text
        return True, req.text


def check_token(token: str, options: Optional[dict] = None) -> Optional[dict]:
    """Verifies a token"""
    if not options:
        options = {}
    decode_options = dict(
        verify_signature=False,
        verify_iat=True,
        verify_nbf=True,
        verify_exp=True,
        verify_iss=False,
        verify_aud=False,
        require_exp=True,
        require_iat=True,
        require_nbf=True)
    decode_options.update(options)
    try:
        data = jwt.decode(token,
                          algorithm='RS512',
                          options=decode_options)
        return data
    except jwt.exceptions.InvalidTokenError:
        return None


def require_mfa(token: dict) -> bool:
    return 'urn:cmi_mfa' in token.get('aud')


def login_mfa(mfa_token: str, raw_token: Optional[str] = None) -> Tuple[bool, str]:
    global __token
    if not __token and not raw_token:
        return False, 'No previous token'
    req = req_sess.post('/frontend/login-mfa',
                        headers={'Authorization': 'Bearer {}'.format(__token)},
                        json=dict(code=mfa_token))
    if req.status_code != 200:
        return False, req.json().get('_error', dict()).get('message', 'Unknown error')
    else:
        __token = req.text
        return True, req.text


def get_privileges(token: dict) -> list:
    return [x[8:] for x in token.get('aud') if x.startswith('urn:cmi_')]
