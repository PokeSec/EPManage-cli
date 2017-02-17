"""
agent.py : Agent APIs

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
from typing import Optional

import click

from epmanage.lib.agent import Agent
from epmanage.lib.agent import AgentAPI
from epmanage.scripts.utils import check_privilege, exit_warning, exit_fail, convert


@click.group()
def agent_group():
    pass


def print_tags(tags: Optional[list]):
    if tags:
        for tag in tags:
            click.echo('[', nl=False)
            click.secho('{name}'.format(**tag), fg='green' if tag.get('type') == 'system' else 'white', nl=False)
            click.echo('] ', nl=False)


def print_agent(agent: Agent, expand=False):
    attrs = agent.attributes()
    if not expand:
        click.secho('{uuid} '.format(**attrs), nl=False, fg='yellow')
        click.echo('{hostname} ({os} {osversion}) '.format(**attrs), nl=False)
        print_tags(attrs.get('tags'))
    else:
        for name, value in attrs.items():
            click.secho('{}'.format(name), nl=False)
            click.echo(' = {}'.format(value))


@agent_group.command()
@check_privilege('ro')
def list():
    data = AgentAPI().list()  # type: list[Agent]
    if not data:
        exit_warning('No data')
    for i, agent in enumerate(data):
        click.echo('[{}] '.format(i), nl=False)
        print_agent(agent)
        click.echo()


@agent_group.command()
@check_privilege('ro')
@click.argument('uuid', required=False)
def print(uuid):
    agent_api = AgentAPI()
    if not uuid:
        data = agent_api.list()  # type: list[Agent]
        if not data:
            exit_warning('No data')
        uuids = dict()
        for i, agent in enumerate(data):
            click.echo('[{}] '.format(i), nl=False)
            print_agent(agent)
            click.echo()
            uuids[i] = agent.attributes()['uuid']
        uuid = uuids[click.prompt('Select an agent', type=click.IntRange(0, len(data)))]

    agent, error = agent_api.get(uuid)
    if not agent:
        exit_fail('Agent not found')

    print_agent(agent, expand=True)


@agent_group.command()
@check_privilege('rw')
@click.argument('uuid')
@click.argument('param')
@click.argument('value')
def set(uuid, param, value):
    agent_api = AgentAPI()
    agent = agent_api.get(uuid)  # type: Agent
    if not agent:
        exit_fail('Agent not found')
    attrs = agent.attributes()

    if not param in attrs:
        exit_fail('Invalid parameter')
    elif agent.is_prop_read_only(param):
        exit_fail('The specified parameter is read-only')

    prop_type = agent.get_prop_type(param).get('type')
    value, error = convert(prop_type, value)
    if not value:
        exit_fail('Invalid value: {}'.format(error))

    ret, error = agent_api.patch(agent, {param: value})
    if ret:
        click.secho('Update successful', fg='green')
    else:
        click.secho('Update error: {}'.format(error), fg='red')


@agent_group.command()
@check_privilege('rw')
@click.argument('uuid')
def delete(uuid):
    agent_api = AgentAPI()
    agent = agent_api.get(uuid)
    if not agent:
        exit_fail('Agent not found')

    if click.confirm('Do you really want to delete this agent?'):
        ret, error = agent_api.delete(agent)
        if ret:
            click.secho('Agent deleted', fg='green')
        else:
            click.secho('Deletion error', fg='red')
