"""
app.py : App management API

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
from typing import List

from epmanage.lib.api import req_sess
from epmanage.lib.eve_api import EveAPI, EveItem


class App(EveItem):
    def __init__(self, data):
        super(App, self).__init__(data)


class AppAPI(EveAPI):
    def __init__(self):
        super(AppAPI, self).__init__('app', App)

    def from_name(self, name: str) -> App:
        return self.get2('name', name)

    def admin_list(self) -> List[str]:
        req = req_sess.get('/admin/apps')
        if req.status_code != 200:
            return []
        else:
            return req.json().get('apps', [])

    def manage(self, name, action):
        req = req_sess.post(
            '/admin/apps/{}'.format(name),
            json=dict(action=action))
        if req.status_code not in [201, 204]:
            return False, req.json()
        else:
            return True, None
