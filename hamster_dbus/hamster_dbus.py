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
import logging

import hamsterlib
from hamsterlib import Category, Activity, Fact
from six import text_type

logger = logging.getLogger('hamster-dbus')


DBUS_SERVICE_NAME = 'org.gnome.hamster_dbus'
DBUS_OBJECT_PATH = '/org/gnome/hamster_dbus'

# setup basic logging
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class HamsterDBusService(dbus.service.Object):
    """A session bus providing access to hamsterlib."""

    def __init__(self, name=None, path=None, bus=None, loop=None):
        self.loop = loop
        self.dbus_name = name or DBUS_SERVICE_NAME
        self.dbus_path = path or DBUS_OBJECT_PATH
        self.bus = dbus.SessionBus()

        bus_name = dbus.service.BusName(name=self.dbus_name, bus=self.bus)
        super(HamsterDBusService, self).__init__(bus_name, self.dbus_path)

        self.controler = hamsterlib.HamsterControl(self._get_config())

    @dbus.service.method('org.gnome.hamster_dbus')#.hello_world')
    def hello_world(self):
        return 'Hello World!'

    # Register signals that can be called by dbus-clients.
    @dbus.service.signal(DBUS_SERVICE_NAME)
    def TagsChanged(self): pass
    def tags_changed(self):
        self.TagsChanged()

    @dbus.service.signal(DBUS_SERVICE_NAME)
    def FactsChanged(self): pass
    def facts_changed(self):
        self.FactsChanged()

    @dbus.service.signal(DBUS_SERVICE_NAME)
    def ActivitiesChanged(self): pass
    def activities_changed(self):
        self.ActivitiesChanged()

    @dbus.service.signal(DBUS_SERVICE_NAME)
    def ToggleCalled(self): pass
    def toggle_called(self):
        self.toggle_called()

    # General Methods
    @dbus.service.method(DBUS_SERVICE_NAME)
    def Quit(self):
        """Shutdown the service."""
        #GLib.MainLoop().quit()
        self.loop.quit()

    # Category Methods
    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='s', out_signature = 'i')
    def AddCategory(self, name):
        """
        Add a new category.

        Args:
            name (str): Name of the new category

        Returns:
            int: PK of the created category or -1 if we failed.
        """

        # It apears that dbus does *not* enforce passed arguments to be of given
        # type. In particular, it is quite possible to pass it an integer which
        # dbus does not even attempt to convert into a string.
        logger.debug(name)
        logger.debug(type(name))
        if not isinstance(name, dbus.String):
            message = _("Name is not a string!")
            logger.error(message)
            result = -1
        else:
            name = text_type(name)
            try:
                category = Category(name)
            except:
                logger.error(sys.exc_info())
                result = -1
                raise TypeError
            else:
                try:
                    category = self.controler.store.categories.save(category)
                except:
                    logger.error(sys.exc_info())
                    result = -1
                    raise ValueError
                else:
                    result = category.pk
                    # [FIXME]
                    # Why 'activities'?
                    self.activities_changed()
        return result




    # Helpers
    def _get_config(self):
        """Get config to be passed to controler."""
        return {
            'store': 'sqlalchemy',
            'day_start': datetime.time(5, 30, 0),
            'fact_min_delta': 60,
            'tmpfile_path': '/tmp/tmpfile.pickle',
            'db_engine': 'sqlite',
            'db_path': ':memory:',
        }



if __name__ == '__main__':
    arg = ""
    if len(sys.argv) > 1:
    	arg = sys.argv[1]

    if arg == "server":
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        myservice = HamsterDBusService(loop=loop)
        # Run needs to be called after we setup our service
        loop.run()
