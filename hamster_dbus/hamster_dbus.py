#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

from __future__ import unicode_literals

from gi.repository import GLib
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys
import datetime

import hamsterlib


class HamsterDBusService(dbus.service.Object):
    """A session bus providing access to hamsterlib."""

    def __init__(self, *args, **kwargs):
        bus_name = dbus.service.BusName('org.gnome.hamster_dbus', bus=dbus.SessionBus())
        bus_path = '/org/gnome/hamster_dbus'
        #super(HamsterDBusService, self).__init__(bus_name, bus_path, *args, **kwargs)
        #dbus_service = HamsterDBusService(bus_name, bus_path)
        dbus.service.Object.__init__(self, bus_name, bus_path, *args, **kwargs)

        self.controler = hamsterlib.HamsterControl(self._get_config())


    def _get_config(self):
        """Get config to be passed to controler."""
        return {
            'store': 'sqlalchemy',
            'day_start': datetime.time(5, 30, 0),
            'fact_min_delta': 60,
            'tmpfile_path': '/tmp/tmpfile.pickle',
            'db_engine': 'sqlite',
            'db_path': '/tmp/hamster-dbus.sqlite',
        }



if __name__ == '__main__':
    arg = ""
    if len(sys.argv) > 1:
    	arg = sys.argv[1]

    if arg == "server":
        DBusGMainLoop(set_as_default=True)
        myservice = HamsterDBusService()
        # Run needs to be called after we setup our service
        GLib.MainLoop().run()
