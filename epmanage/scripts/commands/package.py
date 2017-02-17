"""
package.py : Package APIs

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

import arrow
import click

from epmanage.lib.package import PackageAPI
from epmanage.scripts.utils import check_privilege, exit_warning, exit_fail


@click.group()
def package_group():
    pass


def print_pkg(pkg: dict):
    if pkg.get('osversion'):
        click.echo('{osversion} '.format(**pkg), nl=False)
    if pkg.get('arch'):
        click.echo('{arch} '.format(**pkg), nl=False)
    click.echo('{name}'.format(**pkg))


@package_group.command()
@check_privilege('ro')
def list():
    items = PackageAPI().list()
    if not items:
        exit_warning('No data')

    for item in items:
        click.echo('Packages for ', nl=False)
        click.secho('{os}'.format(**item), fg='green', nl=False)
        click.echo('\t(Generated {})'.format(arrow.get(item.get('date')).humanize()))
        for pkg in item.get('packages'):
            click.echo('  ', nl=False)
            print_pkg(pkg)


@package_group.command()
@check_privilege('ro')
@click.argument('os')
@click.option('--osversion', help='OS version')
@click.option('--arch', help='Architecture')
def download(os, osversion, arch):
    def choose_callback(pkgs):
        for i in range(len(pkgs)):
            click.echo('[{}] '.format(i), nl=False)
            print_pkg(pkgs[i])
        return click.prompt('Select a package', type=click.IntRange(0, len(pkgs)))

    try:
        fname, content = PackageAPI().download(os, osversion, arch, choose_callback)
    except ValueError as exc:
        exit_fail(exc)

    try:
        with open(fname, 'wb') as ofile:
            ofile.write(content)
        click.secho('Download successful : {}'.format(fname), fg='green')
    except OSError as exc:
        exit_fail('Cannot save file to disk: {}'.format(exc))
