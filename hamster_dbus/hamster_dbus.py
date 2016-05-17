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

"""
Most parts of our API do not provide decent input verification and error handling
as most of this would break backwards compability. This is somethin we absolutly
want once we are willing to break the API.
"""

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

    def __init__(self, name=None, path=None, bus=None, loop=None, controler=None):
        self.loop = loop
        self.dbus_name = name or DBUS_SERVICE_NAME
        self.dbus_path = path or DBUS_OBJECT_PATH
        self.bus = dbus.SessionBus()

        bus_name = dbus.service.BusName(name=self.dbus_name, bus=self.bus)
        super(HamsterDBusService, self).__init__(bus_name, self.dbus_path)#, mainloop=loop)

        self.controler = controler or hamsterlib.HamsterControl(self._get_config())

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

        category = Category(name)
        print(type(self.controler.store.categories.save))
        category = self.controler.store.categories.save(category)
        return category.pk

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='is')
    def UpdateCategory(self, pk, name):
        """
        Update a category identified by its pk.

        Args:
            pk (int): PK of the category to be updated.
            name (str): (New) name of the category.

        Returns:
            None
        """

        category = Category(name, pk=pk)
        self.controler.store.categories.save(category)

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='i')
    def RemoveCategory(self, pk):
        """
        Remove a category.

        Args:
            pk (int): PK of the category to be removed.

        Returns:
            None
        """

        category = self.controler.store.categories.get(pk)
        self.controler.store.categories.remove(category)

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='s', out_signature='i')
    def GetCategoryId(self, name):
        """
        Look up a category by its name and return its PK.

        Args:
            name (str): Name of the category to we want the PK of.

        Returns:
            int: PK of the category.
        """
        category = self.controler.categories.get_by_name(name)
        return category.pk

    @dbus.service.method(DBUS_SERVICE_NAME, out_signature='a(is)')
    def GetCategories(self):
        """
        Get all categories.

        Returns:
            list: List of tuples with (category.pk, category.name)
        """
        return [(category.pk, category.name) for category in self.controler.categories.get_all()]

    # Activity Methods
    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='si', out_signature = 'i')
    def AddActivity(self, name, category_pk=-1):
        """
        Add a new activity.

        Args:
            name (str): Name of the new activity
            category_pk (int): PK or -1 (None) of the category for this
            new activity

        Returns:
            int: PK of the new activity.

        Note:
            If we the passed name/category combination already exists we play
            along and return the existing instances pk. This is due to legacy behaviour.
        """

        if category_pk >= 0:
            category = self.controler.store.categories.get(category_pk)
        else:
            category = None
        activity = Activity(name, category=category)
        result = self.controler.store.activities.get_or_create(activity)
        self.activities_changed()
        return result

    # [TODO] This as well does not allow for feedback!
    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='isi')
    def UpdateActivity(self, pk, name, category_pk):
        """
        Update an existing activities values.

        Args:
            pk (int): PK of the activity to be updated.
            name (str): New name of the activity.
            category_id (int): PK of the associated category. -1 if None.

        Returns:
            Nothing
        """
        # [TODO]
        # Add sanity checks for name and PKs. Breaks API!

        if category_pk:
            if category_pk >= 0:
                category = self.controler.store.categories.get(category_pk)
            else:
                category = None

        activity = self.controler.store.activities.get(pk)
        activity.name = name
        activity.category = category

        self.controler.store.activities.save(activity)
        self.activities_changed()

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='i')
    def RemoveActivity(self, pk):
        """Remove an activity.

        Args:
            pk (int): PK of the activity to be removed.

        Returns:
            Nothing.
        """
        activity = self.controler.store.activities.get(pk)
        self.controler.store.activities.delete(activity)
        self.activities_changed()

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='s', out_signature='a(ss)')
    def GetActivities(self, search_term):
        """
        Return a list of activities ready for consumption by autocomplete.

        Args:
            search_term (str):

        Returns:
            list: List of (activity.name, activity.category.name) tuples where each
                tuple represents a matched activity. If an ``category``
                is ``None`` it is represented by an ``empty string``.
                Results are ordered by the mosts recent start time and
                ``lower(activity.name)`` as well as capped at 50 hits.
        """
        activities = []
        for activity in self.controler.store.get_all(search_term=search_term):
            if activity.category is None:
                category = ''
            else:
                category = activity.category.name
            activities.append(activity.name, category)
        return activities

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='sib', out_signature='a{sv}')
    def GetActivityByName(self, activity_name, category_pk, resurrect):
        """
        Get the most recent, preferably non deleted, activity by it's name.

        Args:
            activity (str): ???
            category_pk (int): PK of the activivties category. -1 for None.
            resurrect (bool): ???

        Returns:
            dict: Dictionary with the following stucture or ``{}`` if no such
            name/category combination was found.::

                    {
                    'id': activity.pk,
                    'name': activity.name,
                    'deleted': activity: deleted,
                    'category': activity.category.name
                    }
        """
        # [TODO]
        # Regarding legacy implementation: why 'preferably delted'? Each name/category
        # combination is unique isn't it? As such there should be no two instance
        # where one is deleted and one not.
        activity = self.activities.get_by_composite(activity_name, category_pk)
        # [FIXME]
        # Handle resurrection
        # [FIXME]
        # Handle ``activity.category=None``
        category = self.controler.store.categories.get(category_pk)
        activity = self.controler.store.activities.get_by_composite(activity_name, category)
        return {'id': activity.pk,
                'name': activity.name,
                'deleted': activity.deleted,
                'category': activity.category.name
                }




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
