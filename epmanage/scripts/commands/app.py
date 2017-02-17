"""
apps.py : Apps APIs

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

import click

from epmanage.lib.app import AppAPI, App
from epmanage.scripts.utils import check_privilege, exit_warning, exit_fail


@click.group()
def app_group():
    pass


def print_app(app: App, expand=False):
    attrs = app.attributes()
    if not expand:
        click.secho('{name} '.format(**attrs), nl=False, fg='yellow')
    else:
        for name, value in attrs.items():
            click.secho('{}'.format(name), nl=False)
            click.echo(' = {}'.format(value))


@app_group.command()
@check_privilege('ro')
def list():
    data = AppAPI().list()  # type: List[App]
    if not data:
        exit_warning('No data')
    for i, app in enumerate(data):
        click.echo('[{}] '.format(i), nl=False)
        print_app(app)
        click.echo()


@app_group.command()
@check_privilege('superadmin')
def adminlist():
    app_api = AppAPI()
    data = app_api.list()  # type: List[App]
    if not data:
        exit_warning('No data')
    apps = {x['name']: x for x in data}

    items = app_api.admin_list()
    if not items:
        exit_warning('No apps im adminlist')

    for item in items:
        click.secho(item, fg='green' if item in apps else 'red')


@app_group.command()
@check_privilege('superadmin')
@click.argument('action')
@click.argument('name')
def manage(action: str, name: str):
    result, error = AppAPI().manage(name, action)
    if not result:
        exit_fail(error.get('_error', {}).get('message', 'Unknown error'))
    else:
        click.secho('Success', fg='green')
