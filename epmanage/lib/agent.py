"""
agent.py : Agent management API

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


class Agent(EveItem):
    def __init__(self, data):
        super(Agent, self).__init__(data)


class AgentAPI(EveAPI):
    def __init__(self):
        super(AgentAPI, self).__init__('agent', Agent)
