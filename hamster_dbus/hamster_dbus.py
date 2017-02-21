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

from . import helpers

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

        self.controler = controler or hamsterlib.HamsterControl(helpers._get_config())

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
    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='si', out_signature='i')
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
        return result.pk

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

        if category_pk:
            if category_pk >= 0:
                category = self.controler.store.categories.get(category_pk)
            else:
                category = None

        activity = self.controler.store.activities.get(pk)
        print(activity)
        print(activity.pk)
        activity.name = name
        activity.category = category

        self.controler.store.activities.save(activity)
        self.activities_changed()

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='ii', out_signature = 'b')
    def ChangeCategory(self, pk, category_pk):
        # [FIXME] Verify that we understand what this is for.
        """
        ??? Change an activities category ???
        For reference see __change_category in storage.db.

        All the bizzare shit this is supposed to handle, we cover as part of
        our Activity.update method.

        :param int pk: PK of an activity

        :return: Success status
        :rtype: bool
        """
        # [FIXME]
        # This should be most likely be removed entirely. However, as
        # not to break existing client code, the next best thing would be to
        # just call self.UpdateActivity.
        # However, as UpdateActivity right now can not return any feedback on
        # success/failure which we (sanely) need here to pass on to our caller
        # we are left with duplicating code for now :/
        raise NotImplementedError

        activity = self.activities.get_(pk)
        activity.category = self.categories.get(category_pk)
        return self.activities.save(activity)

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='i')
    def RemoveActivity(self, pk):
        """Remove an activity.

        Args:
            pk (int): PK of the activity to be removed.

        Returns:
            Nothing.
        """
        activity = self.controler.store.activities.get(pk)
        self.controler.store.activities.remove(activity)
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
        raise NotImplementedError
        activities = []
        for activity in self.controler.store.activities.get_all(search_term=search_term):
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
            category_pk (int): PK of the activities category. -1 for None.
            resurrect (bool): ???

        Returns:
            dict: Dictionary with the following structure or ``{}`` if no such
            name/category combination was found.::

                    {
                    'id': activity.pk,
                    'name': activity.name,
                    'deleted': activity: deleted,
                    'category': activity.category.name or ``fallback``
                    }
        """

        if category_pk == -1:
            category = None
        else:
            category = self.controler.store.categories.get(category_pk)
        activity = self.controler.store.activities.get_by_composite(activity_name, category)
        return {'id': activity.pk,
                'name': activity.name,
                'deleted': activity.deleted,
                'category': helpers._represent_category(activity.category, legacy_mode=True),
                }

    # Fact Methods
    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='siib', out_signature='i')
    def AddFact(self, raw_fact, start, end, temporary):
        """
        Take a raw_fact with start/end info and add it to our backend.

        Args:
            raw_fact (str): A 'raw_fact'. See hamsterlib API for format details.
            start (int): Unix-timestamp of the start-datetime.
            end (int): Unix-timestamp of the end-datetime.
            temporary (bool): Who the fuck knows what this is about...
                Even legacy implementation never uses this.

        Returns:
            int: PK of the new Fact or ``0`` if fact is incomplete.
                Legacy hamsters error check is rather moot and pointless. We
                mimic it more for compatibility than anything else.
        """

        fact = Fact.create_from_raw_fact(raw_fact)

        # Explicit trumps implicit.
        if start:
            fact.start = datetime.datetime.utcfromtimestamp(start)
        if end:
            fact.end = datetime.datetime.utcfromtimestamp(end)

        result = self.controler.store.facts.save(fact)
        if not fact.activity or fact.start is None:
            result = 0

        if result:
            self.facts_changed()
        return result

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='isiib', out_signature='i')
    def UpdateFact(self, fact_pk, raw_fact, start, end, temporary):
        """
        Update an existing fact.

        Args:
            fact_pk (int): PK of the fact we want to update.
            raw_fact (str): 'raw fact' String containing details about the
                fact to be changed.
            start (int): Unix-timestamp with start datetime information.
            end (int): Unix-timestamp with end datetime information.
            temporary (bool): Who knows ...

        Returns:
            int: PK of the updated fact.

        Note:
            In line with the original implementation this is more a *replace* than
            an *update* method.
        """

        fact = Fact.create_from_raw_fact(raw_fact)

        # Explicit trumps implicit.
        if start:
            fact.start = datetime.datetime.utcfromtimestamp(start)
        if end:
            fact.end = datetime.datetime.utcfromtimestamp(end)
        fact.pk = fact_pk

        result = self.controler.store.facts.save(fact)
        if result:
            self.facts_changed()
        return result

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='i')
    def RemoveFact(self, fact_pk):
        """
        Remove fact from storage by it's PK

        Args:
            fact_pk (int): PK of the fact to be removed.

        Returns:
            Nothing.
        """

        fact = self.facts.get(fact_pk)
        result = self.controler.store.facts.remove(fact)
        if result:
            self.facts_changed()

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='i', out_signature='(iiissisasii)')
    def GetFact(self, fact_pk):
        """Get fact by id. For output format see ``helpers._hamster_to_dbus_fact``.

        Args:
            fact_pk (int): PK of the fact to be retrieved.

        Returns:
            tuple: A 'dbus_fact'-tuple.

        Note:
            * If ``fact.category=None`` we will return
              ``category_name=unsorted_localized``. This was handled on the db
              level by the legacy implementation. We do it transparently on the
              client level instead.
        """

        fact = self.facts.get(fact_pk)
        return self._hamster_to_dbus_fact(fact)

    @dbus.service.method(DBUS_SERVICE_NAME, in_signature='uus', out_signature='a(iiissisasii)')
    def GetFacts(self, start_date, end_date, filter_term):
        """
        Gets facts between the day of start_date and the day of end_date.

        Args:
            start_date (int): Unix-timestamp for start of timeframe. Use 0 for today.
            end_date (int): Unix-timestamp for end of timeframe. Use 0 for today.
            filter_term (str): Only consider ``Facts`` with this string as part of their
                associated ``Activity.name``

        Returns:
            list: A list of ``helpers.DBusFact``-tuples.
                For details on those, please see ``helpers._hamster_to_dbus_fact``.

        Note:
            Our ``hamsterlib`` manager method is actually more flexible and would allow
            for ``datetime.datetime`` or ``datetime.time`` instances instead of just
            ``datetime.date`` instances for ``start`` and ``end``. But for compatibility
            reasons we stick with the simpler legacy version for now.
        """

        # Explicit trumps implicit.
        if start_date:
            start = datetime.datetime.utcfromtimestamp(start_date).date()
        elif start_date == 0:
            start = datetime.date.today()

        if end_date:
            end = datetime.datetime.utcfromtimestamp(end_date).date()
        elif end_date == 0:
            emd = datetime.date.today()
        return [self.to_dbus_fact(fact) for fact in self.controler.store.facts.get_all(
            start, end, search_term)]

    @dbus.service.method(DBUS_SERVICE_NAME, out_signature='a(iiissisasii)')
    def GetTodaysFacts(self):
        """
        Gets facts of today, respecting hamster day_start, day_end settings.

        Returns:
            list: A list of ``helpers.DBusFact``-tuples.
                For details on those, please see ``helpers._hamster_to_dbus_fact``.

        Note:
            This only returns proper facts and will not include any ongoing fact!
        """
        return [to_dbus_fact(fact) for fact in self.controler.store.facts.get_today()]



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
