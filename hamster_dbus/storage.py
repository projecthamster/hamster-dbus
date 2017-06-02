#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017 Eric Goller <eric.goller@ninjaduck.solutions>

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
This modules provides dbus backend conforming to the ``hamster_lib.storage`` API.

Using this module allows clients direct all of their storage backend calls against
a corresponding dbus service.
"""

# Whilst it usually preferred to inherit from ``hamster_lib.storage`` and just
# implement the specific functional backend methods such an approach would have
# meant that the mirroring dbus-service would have to export quite a few
# 'private' manager methods.  For this reason we opted against it and instead
# implement the relevant public manager methods 'from scratch'. The price for
# that is that we duplicate errorhandling/sanity check code.


from __future__ import absolute_import, unicode_literals

import datetime
from gettext import gettext as _

import dbus
import hamster_lib.objects as lib_objects
import hamster_lib.storage as lib_storage
from future.utils import python_2_unicode_compatible
from six import text_type

import hamster_dbus.helpers as helpers


@python_2_unicode_compatible
class DBusStore(lib_storage.BaseStore):
    """Store class for hamster-dbus storage backend."""

    def __init__(self, config, bus=None):
        """
        Initialize a new instance.

        Args:
            config (dict): Dictionary containing config data.
            bus (dbus.bus.BusConnection, optional): Connection to be used when
            querying dbus objects. If ``None``, ``dbus.SessionBus()`` will be
            used.

        Returns:
            DBusStore: DBusStore instance.
        """
        if bus is None:
            bus = dbus.SessionBus()
        self._bus = bus
        self.config = config
        self.categories = CategoryManager(self._bus)
        self.activities = ActivityManager(self._bus)
        self.tags = TagManager(self._bus)
        self.facts = FactManager(self._bus)

    def cleanup(self):
        """Teardown chores."""
        return None


@python_2_unicode_compatible
class CategoryManager(object):
    """Class to handle categories."""

    def __init__(self, bus):
        """
        Instantiate class.

        Args:
            bus (dbus.bus.BusConnection): Connection to query against.
        """
        bus_name = 'org.projecthamster.HamsterDBus'
        object_path = '/org/projecthamster/HamsterDBus/CategoryManager'
        interface_name = 'org.projecthamster.HamsterDBus.CategoryManager1'
        dbus_object = bus.get_object(bus_name, object_path)
        self._interface = dbus.Interface(dbus_object, interface_name)

    def save(self, category):
        """
        Save a Category.

        Args:
            category (hamster_lib.Category): Category instance to be saved.

        Returns:
            hamster_lib.Category: Saved Category

        Raises:
            TypeError: If the ``category`` parameter is not a valid ``Category`` instance.
        """
        if not isinstance(category, lib_objects.Category):
            message = _("You need to pass a hamster category")
            raise TypeError(message)

        dbus_category = helpers.hamster_to_dbus_category(category)
        result = self._interface.Save(dbus_category)
        return helpers.dbus_to_hamster_category(result)

    def get_or_create(self, category):
        """
        Check if we already got a category with that name, if not create one.

        For details see the corresponding method in ``hamster_lib.storage``.

        Args:
            category (hamster_lib.Category or None): The categories.

        Returns:
            hamster_lib.Category or None: The retrieved or created category. Either way,
                the returned Category will contain all data from the backend, including
                its primary key.

        Raises:
            TypeError: If ``category`` is not a ``lib_objects.Category`` instance.
        """
        if not isinstance(category, lib_objects.Category):
            message = _("You need to pass a hamster category")
            raise TypeError(message)

        dbus_category = helpers.hamster_to_dbus_category(category)
        result = self._interface.GetOrCreate(dbus_category)
        return helpers.dbus_to_hamster_category(result)

    def remove(self, category):
        """
        Remove a category.

        Any ``Activity`` referencing the passed category will be set to
        ``Activity().category=None``.

        Args:
            category (hamster_lib.Category): Category to be updated.

        Returns:
            None: If everything went ok.

        Raises:
            TypeError: If category passed is not an hamster_lib.Category instance.
        """
        if not isinstance(category, lib_objects.Category):
            message = _("You need to pass a hamster category")
            raise TypeError(message)

        self._interface.Remove(category.pk)
        return None

    def get(self, pk):
        """
        Get an ``Category`` by its primary key.

        Args:
            pk (int): Primary key of the ``Category`` to be fetched.

        Returns:
            hamster_lib.Category: ``Category`` with given primary key.
        """
        result = self._interface.Get(int(pk))
        return helpers.dbus_to_hamster_category(result)

    def get_by_name(self, name):
        """
        Look up a category by its name.

        Args:
            name (str): Unique name of the ``Category`` to we want to fetch.

        Returns:
            hamster_lib.Category: ``Category`` with given name.
        """
        result = self._interface.GetByName(name)
        return helpers.dbus_to_hamster_category(result)

    def get_all(self):
        """
        Return a list of all categories.

        Returns:
            list: List of ``Categories``, ordered by ``lower(name)``.
        """
        result = self._interface.GetAll()
        return [helpers.dbus_to_hamster_category(category) for category in result]


@python_2_unicode_compatible
class ActivityManager(object):
    """Class to handle activities."""

    def __init__(self, bus):
        """
        Instantiate class.

        Args:
            bus (dbus.bus.BusConnection): Connection to query against.
        """
        bus_name = 'org.projecthamster.HamsterDBus'
        object_path = '/org/projecthamster/HamsterDBus/ActivityManager'
        interface_name = 'org.projecthamster.HamsterDBus.ActivityManager1'
        dbus_object = bus.get_object(bus_name, object_path)
        self._interface = dbus.Interface(dbus_object, interface_name)

    def save(self, activity):
        """
        Save an Activivty.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        if not isinstance(activity, lib_objects.Activity):
            message = _("You need to pass a ``hamster_lib.objects.Activity`` instance")
            raise TypeError(message)

        dbus_activity = helpers.hamster_to_dbus_activity(activity)
        result = self._interface.Save(dbus_activity)
        return helpers.dbus_to_hamster_activity(result)

    def get_or_create(self, activity):
        """
        Convenience method to either get an activity matching the specs or create a new one.

        For details see the corresponding method in ``hamster_lib.storage``.

        Args:
            activity (hamster_lib.Activity): The activity we want.

        Returns:
            hamster_lib.Activity: The retrieved or created activity

        Raises:
            TypeError: If ``activity`` is not a ``lib_objects.Activity`` instance.
        """
        if not isinstance(activity, lib_objects.Activity):
            message = _("You need to pass a ``hamster_lib.objects.Activity`` instance")
            raise TypeError(message)

        dbus_activity = helpers.hamster_to_dbus_activity(activity)
        result = self._interface.GetOrCreate(dbus_activity)
        return helpers.dbus_to_hamster_activity(result)

    def remove(self, activity):
        """
        Remove an ``Activity`` from the database.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        if not isinstance(activity, lib_objects.Activity):
            message = _("You need to pass a ``hamster_lib.objects.Activity`` instance")
            raise TypeError(message)

        dbus_activity = helpers.hamster_to_dbus_activity(activity)
        self._interface.Remove(dbus_activity.pk)
        return True

    def get(self, pk):
        """
        Return an activity based on its primary key.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        result = self._interface.Get(pk)
        return helpers.dbus_to_hamster_activity(result)

    def get_by_composite(self, name, category):
        """
        Lookup for unique 'name/category.name'-composite key.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        if not (isinstance(category, lib_objects.Category) or (category is None)):
            message = _("You need to pass a hamster_lib.objects.Category instance or None")
            raise TypeError(message)

        dbus_category = helpers.hamster_to_dbus_category(category)
        name = text_type(name)
        result = self._interface.GetByComposite(name, dbus_category)
        return helpers.dbus_to_hamster_activity(result)

    def get_all(self, category=False, search_term=''):
        """
        Return all matching activities.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        if isinstance(category, lib_objects.Category):
            category = category.pk
        elif category is None:
            category = -1
        elif category is False:
            category = -2
        else:
            message = _(
                "'category' needs to be either a 'hamster_lib.objects.Category' instance,"
                " 'False' or 'None'."
            )
            raise TypeError(message)

        search_term = text_type(search_term)

        result = self._interface.GetAll(category, search_term)
        return [helpers.dbus_to_hamster_activity(activity) for activity in result]


@python_2_unicode_compatible
class TagManager(object):
    """Class to handle tags."""

    def __init__(self, bus):
        """
        Instantiate class.

        Args:
            bus (dbus.bus.BusConnection): Connection to query against.
        """
        bus_name = 'org.projecthamster.HamsterDBus'
        object_path = '/org/projecthamster/HamsterDBus/TagManager'
        interface_name = 'org.projecthamster.HamsterDBus.TagManager1'
        dbus_object = bus.get_object(bus_name, object_path)
        self._interface = dbus.Interface(dbus_object, interface_name)

    def save(self, tag):
        """
        Save a tag.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        if not isinstance(tag, lib_objects.Tag):
            message = _("You need to pass a ``hamster_lib.objects.Tag`` instance")
            raise TypeError(message)

        dbus_tag = helpers.hamster_to_dbus_tag(tag)
        result = self._interface.Save(dbus_tag)
        return helpers.dbus_to_hamster_tag(result)

    def get_or_create(self, tag):
        """
        Check if we already got a tag with that name, if not create one.

        For details see the corresponding method in ``hamster_lib.storage``.

        Args:
            tag (hamster_lib.Tag): The tag we want.

        Returns:
            hamster_lib.Tag: The retrieved or created tag.

        Raises:
            TypeError: If ``tag`` is not a ``lib_objects.Tag`` instance.
        """
        if not isinstance(tag, lib_objects.Tag):
            message = _("You need to pass a ``hamster_lib.objects.Tag`` instance")
            raise TypeError(message)

        dbus_tag = helpers.hamster_to_dbus_tag(tag)
        result = self._interface.GetOrCreate(dbus_tag)
        return helpers.dbus_to_hamster_tag(result)

    def remove(self, tag):
        """
        Remove a tag.

        Any ``Fact`` referencing the passed tag will have this tag removed.

        Args:
            tag (hamster_lib.Tag): Tag to be updated.

        Returns:
            None: If everything went ok.

        Raises:
            TypeError: If tag passed is not an hamster_lib.Tag instance.
        """
        if not isinstance(tag, lib_objects.Tag):
            message = _("You need to pass a hamster tag")
            raise TypeError(message)

        self._interface.Remove(tag.pk)
        return None

    def get(self, pk):
        """
        Get an ``Tag`` by its primary key.

        Args:
            pk (int): Primary key of the ``Tag`` to be fetched.

        Returns:
            hamster_lib.Tag: ``Tag`` with given primary key.
        """
        result = self._interface.Get(int(pk))
        return helpers.dbus_to_hamster_tag(result)

    def get_by_name(self, name):
        """
        Look up a tag by its name.

        Args:
            name (text_type): Unique name of the ``Tag`` to we want to fetch.

        Returns:
            hamster_lib.Tag: ``Tag`` with given name.
        """
        result = self._interface.GetByName(name)
        return helpers.dbus_to_hamster_tag(result)

    def get_all(self):
        """
        Return a list of all tags.

        Returns:
            list: List of ``Tags``, ordered by ``lower(name)``.
        """
        result = self._interface.GetAll()
        return [helpers.dbus_to_hamster_tag(tag) for tag in result]


@python_2_unicode_compatible
class FactManager(object):
    """Class to handle facts."""

    def __init__(self, bus):
        """
        Instantiate class.

        Args:
            bus (dbus.bus.BusConnection): Connection to query against.
        """
        bus_name = 'org.projecthamster.HamsterDBus'
        object_path = '/org/projecthamster/HamsterDBus/FactManager'
        interface_name = 'org.projecthamster.HamsterDBus.FactManager1'
        dbus_object = bus.get_object(bus_name, object_path)
        self._interface = dbus.Interface(dbus_object, interface_name)

    def save(self, fact):
        """
        Save a Fact.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        if not isinstance(fact, lib_objects.Fact):
            message = _("You need to pass a ``hamster_lib.objects.Fact`` instance")
            raise TypeError(message)

        dbus_fact = helpers.hamster_to_dbus_fact(fact)
        result = self._interface.Save(dbus_fact)
        return helpers.dbus_to_hamster_fact(result)

    def remove(self, fact):
        """
        Remove a Fact.

        For details see the corresponding method in ``hamster_lib.storage``.
        """
        if not isinstance(fact, lib_objects.Fact):
            message = _("You need to pass a ``hamster_lib.objects.Fact`` instance")
            raise TypeError(message)

        self._interface.Remove(fact.pk)

    def get(self, pk):
        """
        Return a ``Fact`` by its primary key.

        Args:
            pk (int): Primary key of the ``Fact to be retrieved``.

        Returns:
            hamster_lib.Fact: The ``Fact`` corresponding to the primary key.
        """
        result = self._interface.Get(int(pk))
        return helpers.dbus_to_hamster_fact(result)

    def get_all(self, start=None, end=None, filter_term=''):
        """
        Return all facts within a given timeframe.

        The 'timeframe' begins at the begining of ``start`` and
        concludes at the end of ``end``.

        Args:
            start (datetime.datetime, datetime.date, datetime.time or None, optional): Consider
                only Facts starting at or after this date. Alternatively you can
                also pass a ``datetime.datetime`` object in which case its own
                time will be considered instead of the default ``day_start``
                or a ``datetime.time`` which will be considered as today.
                Defaults to ``None``.
            end (datetime.datetime, datetime.date, datetime.time or None, optional): Consider
                only Facts ending before or at this date. Alternatively you can
                also pass a ``datetime.datetime`` object in which case its own
                time will be considered instead of the default ``day_start``
                or a ``datetime.time`` which will be considered as today.
                Defaults to ``None``.
            filter_term (str, optional): Only consider ``Facts`` with this
                string as part of their associated ``Activity.name``

        Returns:
            list: List of ``Fact``s matching given specifications.

        Raises:
            TypeError: If ``start`` or ``end`` are not ``datetime.date``, ``datetime.time`` or
                ``datetime.datetime`` objects.
            ValueError: If ``end`` is before ``start``.

        Note:
            * This public function only provides some sanity checks and normalization. The actual
                backend query is handled by ``_get_all``.
            * ``search_term`` should be prefixable with ``not`` in order to invert matching.
            * This does only return proper facts and does not include any existing 'ongoing fact'.
        """
        if not (isinstance(start, datetime.datetime) or isinstance(start, datetime.date) or (
                isinstance(start, datetime.time) or (start is None))):
            raise TypeError
        if not (isinstance(end, datetime.datetime) or isinstance(end, datetime.date) or (
                isinstance(end, datetime.time) or (end is None))):
            raise TypeError

        if start and end and (end <= start):
            message = _("End value can not be earlier than start!")
            raise ValueError(message)

        start = helpers.datetime_to_text(start)
        end = helpers.datetime_to_text(end)
        filter_term = text_type(filter_term)
        result = self._interface.GetAll(start, end, filter_term)
        return [helpers.dbus_to_hamster_fact(fact) for fact in result]

    def get_today(self):
        """
        Return all facts for today, while respecting ``day_start``.

        Returns:
            list: List of ``Fact`` instances.

        Note:
            * This does only return proper facts and does not include any existing 'ongoing fact'.
        """
        result = self._interface.GetToday()
        return [helpers.dbus_to_hamster_fact(fact) for fact in result]

    def stop_tmp_fact(self):
        """
        Stop current 'ongoing fact'.

        Returns:
            hamster_lib.Fact: The stored fact.

        Raises:
            ValueError: If there is no currently 'ongoing fact' present.
        """
        result = self._interface.StopTmpFact()
        return helpers.dbus_to_hamster_fact(result)

    def cancel_tmp_fact(self):
        """
        Provide a way to stop an 'ongoing fact' without saving it in the backend.

        Returns:
            None: If everything worked as expected.

        Raises:
            KeyError: If no ongoing fact is present.
        """
        self._interface.CancelTmpFact()
        return None

    def get_tmp_fact(self):
        """
        Provide a way to retrieve any existing 'ongoing fact'.

        Returns:
            hamster_lib.Fact: An instance representing our current 'ongoing fact'.capitalize

        Raises:
            KeyError: If no ongoing fact is present.
        """
        result = self._interface.GetTmpFact()
        return helpers.dbus_to_hamster_fact(result)
