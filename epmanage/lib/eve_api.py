"""
eve_api.py : EVE API Base

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
import warnings
from collections import OrderedDict

from epmanage.lib.api import req_sess


class EveItem(object):
    schema = None

    def __init__(self, data):
        self._data = data

    def attributes(self) -> dict:
        out = OrderedDict()
        for prop in sorted(self.schema.keys()):
            out[prop] = self._data.get(prop)
        return out

    def is_prop_read_only(self, prop: str) -> bool:
        return self.schema.get(prop, {}).get('readonly')

    def get_prop_type(self, prop: str) -> dict:
        return self.schema.get(prop, {})

    def get_url(self):
        try:
            return self._data['_links']['self']['href']
        except KeyError:
            return None

    @property
    def etag(self):
        return self._data['_etag']

    def update(self, data: dict):
        self._data.update(data)


class EveAPI(object):
    def __init__(self, model, item_cls):
        self._model = model
        self._item_cls = item_cls
        req = req_sess.get('/schema')
        if req.status_code != 200:
            warnings.warn('Cannot fetch schema')
        else:
            self._schema = req.json().get(self._model)
            item_cls.schema = self._schema

    def list(self, filter=None) -> list:
        params = dict()
        if filter:
            params = dict(filter=filter)
        req = req_sess.get(
            '/{}'.format(self._model),
            params=params)
        if req.status_code != 200:
            return []

        items = req.json().get('_items')

        return [self._item_cls(item) for item in items]

    def get(self, info):
        req = req_sess.get('/{}/{}'.format(self._model, info))
        if req.status_code != 200:
            return None, req.json()
        return self._item_cls(req.json()), None

    def get2(self, attr, value):
        items = self.list('{}={}'.format(attr, value))
        if len(items) == 1:
            return items[0]

    def patch(self, item: EveItem, params: dict):
        req = req_sess.patch(
            '/{}'.format(item.get_url()),
            json=params,
            headers={
                'If-Match': item.etag
            })
        if req.status_code == 200:
            item.update(req.json())
            return True, None
        else:
            return False, req.json()

    def delete(self, item: EveItem):
        req = req_sess.delete(
            '/{}'.format(item.get_url()),
            headers={
                'If-Match': item.etag
            })
        if req.status_code == 204:
            return True, None
        else:
            return False, req.json()
