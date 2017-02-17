"""
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
import sys
from functools import update_wrapper

import arrow
import click

from epmanage.lib.api import setup_auth
from epmanage.lib.auth import get_privileges


def echo_fail(msg: str):
    command = click.get_current_context().info_name
    click.secho('{} failed: '.format(command), nl=False, fg='red')
    click.echo(msg)


def exit_fail(msg: str):
    echo_fail(msg)
    sys.exit(1)


def echo_warning(msg: str):
    command = click.get_current_context().info_name
    click.secho('{} error: '.format(command), nl=False, fg='yellow')
    click.echo(msg)


def exit_warning(msg: str):
    echo_warning(msg)
    sys.exit(1)


def check_privilege(privilege):
    def decorator(f):
        @click.pass_context
        def new_func(ctx, *args, **kwargs):
            token = click.get_current_context().obj['token']
            if not token:
                exit_fail('Invalid token')
            if not privilege in get_privileges(token):
                exit_fail('Insufficient permissions')
            setup_auth(click.get_current_context().obj['raw_token'])
            return ctx.invoke(f, *args, **kwargs)

        return update_wrapper(new_func, f)

    return decorator


def convert(prop_type: str, value: str):
    if prop_type == 'string':
        return value, None
    elif prop_type == 'integer':
        try:
            return int(value)
        except ValueError as exc:
            return None, exc
    elif prop_type == 'boolean':
        return value.lower() == 'true'
    elif prop_type == 'datetime':
        return arrow.get(value).isoformat()
    elif prop_type == 'list':
        return value.split('|')
    # FIXME: dict
    # FIXME: media
    else:
        return None, 'This type cannot be edited'
