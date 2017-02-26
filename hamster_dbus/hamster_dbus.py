#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Provide a trivial service implementation to export ``hamster-lib`` functionality."""

# This file is part of 'hamster-dbus'.
#
# 'hamster-dbus' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-dbus' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  'hamster-dbus'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import sys

import hamster_lib
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from . import helpers, objects

if __name__ == '__main__':
    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

    if arg == "server":
        controller = hamster_lib.HamsterControl(helpers.get_config())
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        objects.HamsterDBus(loop)
        objects.CategoryManager(controller)
        objects.ActivityManager(controller)
        objects.FactManager(controller)
        # Run needs to be called after we setup our service
        loop.run()
