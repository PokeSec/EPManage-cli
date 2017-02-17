"""
user.py : User management API

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

from epmanage.lib.eve_api import EveAPI, EveItem


class User(EveItem):
    def __init__(self, data):
        super(User, self).__init__(data)


class UserAPI(EveAPI):
    def __init__(self):
        super(UserAPI, self).__init__('user', User)

    def from_email(self, email: str) -> User:
        return self.get2('email', email)
