"""
cli.py : EPManage-cli

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
from pathlib import Path
from typing import Optional

import arrow
import click

import epmanage.lib.auth
from epmanage.lib.api import req_sess
from epmanage.lib.user import UserAPI
from epmanage.scripts.utils import exit_fail, echo_fail, check_privilege, convert
from .commands.agent import agent_group
from .commands.app import app_group
from .commands.package import package_group
from .commands.user import user_group


@click.group()
@click.option('--tokenfile', envvar='EPMANAGE-TOKEN', default='.token', type=click.Path(exists=False, dir_okay=False),
              help='Location of the token')
@click.option('--baseurl', envvar='EPMANAGE-URL', help='API base url')
def cli(tokenfile, baseurl):
    click.get_current_context().obj = dict()
    tokenfile = Path(tokenfile)
    if tokenfile.exists():
        click.get_current_context().obj['raw_token'] = tokenfile.read_text()
        click.get_current_context().obj['token'] = epmanage.lib.auth.check_token(
            click.get_current_context().obj['raw_token'])
    req_sess.base_url = baseurl


@cli.command()
def version():
    click.echo('EPManage-cli ', nl=False)
    click.secho('0.0.1', fg='green')


@cli.command()
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--mfa', help='MFA token')
@click.argument('tokenfile', envvar='EPMANAGE-TOKEN', default='.token', type=click.File('w'))
def auth(email: str, password: str, mfa: Optional[str], tokenfile):
    status, rsp = epmanage.lib.auth.auth(email, password)
    if not status:
        exit_fail(rsp)
    token = epmanage.lib.auth.check_token(rsp)
    if not token:
        exit_fail('Invalid token')

    if epmanage.lib.auth.require_mfa(token):
        mfa_status = False
        exp = arrow.get(token.get('exp'))
        if mfa:
            mfa_status, rsp = epmanage.lib.auth.login_mfa(mfa)
            if not mfa_status:
                exit_fail(rsp)
        while not mfa_status and exp > arrow.utcnow():
            mfa = click.prompt("Enter MFA token")
            mfa_status, rsp = epmanage.lib.auth.login_mfa(mfa)
            if not mfa_status:
                echo_fail(rsp)

        if not mfa_status:
            exit_fail('Invalid MFA token')
        token = epmanage.lib.auth.check_token(rsp)
        if not token:
            exit_fail('Invalid token')

    click.secho('Auth success', fg='green')
    exp = arrow.get(token.get('exp'))
    click.echo('  token expires {} ({})'.format(exp.humanize(), exp))
    click.echo('  privileges: {}'.format(','.join(epmanage.lib.auth.get_privileges(token))))

    tokenfile.write(rsp)


@cli.command()
def check_token():
    token = click.get_current_context().obj['token']
    if not token:
        exit_fail('Invalid token')
    click.secho('Valid token', fg='green')
    exp = arrow.get(token.get('exp'))
    click.echo('  token expires {} ({})'.format(exp.humanize(), exp))
    click.echo('  privileges: {}'.format(','.join(epmanage.lib.auth.get_privileges(token))))


@cli.command()
@check_privilege('ro')
@click.argument('param', required=False)
@click.argument('value', required=False)
def profile(param, value):
    token = click.get_current_context().obj['token']
    user_id = token['sub']
    user_api = UserAPI()
    user, error = user_api.get(user_id)
    if not user:
        exit_fail('Cannot get profile, {}'.format(error))
    attrs = user.attributes()

    if param and value:
        # EDIT
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
    else:
        # Display
        for name, value in attrs.items():
            click.secho('{}'.format(name), nl=False)
            click.echo(' = {}'.format(value))


cli.add_command(agent_group, name='agent')
cli.add_command(app_group, name='app')
cli.add_command(package_group, name='package')
cli.add_command(user_group, name='user')

if __name__ == '__main__':
    cli()
