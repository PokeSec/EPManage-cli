"""
user.py : User APIs

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

from epmanage.lib.user import User
from epmanage.lib.user import UserAPI
from epmanage.scripts.utils import check_privilege, exit_warning, exit_fail, convert


@click.group()
def user_group():
    pass


def print_user(user: User, expand=False):
    attrs = user.attributes()
    if not expand:
        click.secho('{email} '.format(**attrs), nl=False, fg='yellow')
    else:
        for name, value in attrs.items():
            click.secho('{}'.format(name), nl=False)
            click.echo(' = {}'.format(value))


@user_group.command()
@check_privilege('admin')
def list():
    data = UserAPI().list()  # type: List[User]
    if not data:
        exit_warning('No data')
    for i, user in enumerate(data):
        click.echo('[{}] '.format(i), nl=False)
        print_user(user)
        click.echo()


@user_group.command()
@check_privilege('admin')
@click.argument('email', required=False)
def print(email):
    user_api = UserAPI()
    if not email:
        data = user_api.list()  # type: List[User]
        if not data:
            exit_warning('No data')
        emails = dict()
        for i, user in enumerate(data):
            click.echo('[{}] '.format(i), nl=False)
            print_user(user)
            click.echo()
            emails[i] = user.attributes()['email']
        email = emails[click.prompt('Select an user', type=click.IntRange(0, len(data)))]

    user, error = user_api.from_email(email)
    if not user:
        exit_fail('User not found')

    print_user(user, expand=True)


@user_group.command()
@check_privilege('admin')
@click.argument('email')
@click.argument('param')
@click.argument('value')
def set(email, param, value):
    user_api = UserAPI()
    user = user_api.from_email(email)  # type: User
    if not user:
        exit_fail('User not found')
    attrs = user.attributes()

    if not param in attrs:
        exit_fail('Invalid parameter')
    elif user.is_prop_read_only(param):
        exit_fail('The specified parameter is read-only')

    prop_type = user.get_prop_type(param).get('type')
    value, error = convert(prop_type, value)
    if not value:
        exit_fail('Invalid value: {}'.format(error))

    ret, error = user_api.patch(user, {param: value})
    if ret:
        click.secho('Update successful', fg='green')
    else:
        click.secho('Update error: {}'.format(error), fg='red')


@user_group.command()
@check_privilege('rw')
@click.argument('email')
def delete(email):
    user_api = UserAPI()
    user = user_api.from_email(email)
    if not user:
        exit_fail('User not found')

    if click.confirm('Do you really want to delete this user?'):
        ret, error = user_api.delete(user)
        if ret:
            click.secho('User deleted', fg='green')
        else:
            click.secho('Deletion error', fg='red')
