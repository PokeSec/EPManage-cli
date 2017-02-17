"""
package.py : Package management API

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

import re
from typing import Optional

from epmanage.lib.api import req_sess


class PackageAPI(object):
    def __init__(self):
        pass

    def list(self) -> list:
        req = req_sess.get('/frontend/packages')
        if req.status_code != 200:
            return []

        items = req.json().get('data')
        return items

    def download(self, os: str, osversion: Optional[str], arch: Optional[str], choose_callback=None):
        items = self.list()
        try:
            item = next(x for x in items if x.get('os') == os)
        except StopIteration:
            item = None
        if not item:
            raise ValueError('Unknown os "{}"'.format(os))

        pkgs = []
        for pkg in item.get('packages'):
            if osversion and pkg.get('osversion') != osversion:
                continue
            if arch and pkg.get('arch') != arch:
                continue
            pkgs.append(pkg)
        if len(pkgs) == 0:
            raise ValueError('No package found')
        elif len(pkgs) == 1:
            pkg = pkgs[0]
        elif callable(choose_callback):
            index = choose_callback(pkgs)
            pkg = pkgs[index]
        else:
            raise ValueError('More than one package match')

        req = req_sess.get('{}'.format(pkg['url']))
        if req.status_code != 200:
            raise ValueError('Cannot download package')

        fname = re.findall("filename=([^/]+)", req.headers.get('content-disposition', ''))
        if len(fname) != 1:
            raise ValueError('Invalid response from server (no filename)')
        fname = fname[0]
        return fname, req.content
