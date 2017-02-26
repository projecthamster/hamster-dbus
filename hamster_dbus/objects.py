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
A basic dbus service that exposes a subset up hamster-lib.

Most of the methods exposed here are just 'proxies' for the corresponding
``hamster-lib.storage``-manager methods. For details on arguments and semantics
please also refer to their documentation as we want to avoid duplication).

Capitalization violates PEP8 due to dbus specifications on method names
(https://dbus.freedesktop.org/doc/dbus-api-design.html).
"""
# I still do not understand dbus objects completely so for now there is only the
# main ``HamsterDBus`` object. Object specific managers are implemented as
# separate interfaces to provide as least some degree of grouping/namespaceing.
# Currently hamster-lib objects need to be converted into something that can be
# passed over dbus. Future iteration should revisit this and see if we can
# expose those objects as dbus objects and consequently just pass those.

# If the ``dbus.service.method`` decorator spans multiple lines we need to add
# the ``   # NOQA`` afterwards instead of the actual function definition.
from __future__ import absolute_import, unicode_literals

import dbus
import dbus.service
import hamster_lib

from . import helpers

DBUS_CATEGORIES_INTERFACE = 'org.projecthamster.HamsterDBus.CategoryManager1'
DBUS_ACTIVITIES_INTERFACE = 'org.projecthamster.HamsterDBus.ActivityManager1'
DBUS_FACTS_INTERFACE = 'org.projecthamster.HamsterDBus.FactManager1'


def _get_dbus_bus_name():
    """Return the bus name."""
    # We wrap this in a function instead of a constant to avoid instant
    # instantiation if we use this module as a library.
    return dbus.service.BusName(
        name='org.projecthamster.HamsterDBus',
        bus=dbus.SessionBus()
    )


class HamsterDBus(dbus.service.Object):
    """A dbus object providing access to general hamster-lib capabilities."""

    # [FIXME]
    # 'controller still needed?
    def __init__(self, loop):
        """Initialize main DBus object."""
        self._loop = loop

        super(HamsterDBus, self).__init__(
            bus_name=_get_dbus_bus_name(),
            object_path='/org/projecthamster/HamsterDBus',
        )

    @dbus.service.method('org.projecthamster.HamsterDBus')
    def Quit(self):  # NOQA
        """Shutdown the service."""
        self._loop.quit()


class CategoryManager(dbus.service.Object):
    """CategoryManager object to be exposed via DBus."""

    def __init__(self, controller):
        """Initialize category manager object."""
        self._controller = controller

        super(CategoryManager, self).__init__(
            bus_name=_get_dbus_bus_name(),
            object_path='/org/projecthamster/HamsterDBus/CategoryManager',
        )

    # [FIXME]
    # Missing ``hamster_lib.CategoryManager`` methods that still need to be implemented:
    # ``get_or_create``.

    @dbus.service.method(DBUS_CATEGORIES_INTERFACE, in_signature='(is)', out_signature='(is)')
    def Save(self, category_tuple):  # NOQA
        """
        Save category.

        Args:
            category_tuple: hamster_lib.Category tuple.

        Returns:
            tuple: ``(category.pk, category.name)`` tuple.
        """
        category = helpers.dbus_to_hamster_category(category_tuple)
        category = self._controller.store.categories.save(category)
        return helpers.hamster_to_dbus_category(category)

    @dbus.service.method(DBUS_CATEGORIES_INTERFACE, in_signature='i')
    def Remove(self, pk):  # NOQA
        """
        Remove a category.

        Args:
            pk (int): PK of the category to be removed.

        Returns:
            None: Nothing.
        """
        # [TODO]
        # Once LIB-239 has been solved, we should be able to skip extra category
        # retrieval.
        category = self._controller.store.categories.get(pk)
        self._controller.store.categories.remove(category)
        return None

    @dbus.service.method(DBUS_CATEGORIES_INTERFACE, in_signature='s', out_signature='(is)')
    def GetByName(self, name):  # NOQA
        """
        Look up a category by its name and return its PK.

        Args:
            name (str): Name of the category to we want the PK of.

        Returns:
            tuple: hamster_lib.Category tuple.
        """
        category = self._controller.categories.get_by_name(name)
        return helpers.hamster_to_dbus_category(category)

    @dbus.service.method(DBUS_CATEGORIES_INTERFACE, out_signature='a(is)')
    def GetAll(self):  # NOQA
        """
        Get all categories.

        Returns:
            list: List of tuples with (category.pk, category.name)
        """
        categories = self._controller.categories.get_all()
        return [helpers.hamster_to_dbus_category(category) for category in categories]


class ActivityManager(dbus.service.Object):
    """ActivityManager object to be exposed via DBus."""

    def __init__(self, controller):
        """Initialize activity manager object."""
        self._controller = controller

        super(ActivityManager, self).__init__(
            bus_name=_get_dbus_bus_name(),
            object_path='/org/projecthamster/HamsterDBus/ActivityManager',
        )

    @dbus.service.method(DBUS_ACTIVITIES_INTERFACE, in_signature='(is(is)b)',
        out_signature='(is(is)b)')  # NOQA
    def Save(self, activity_tuple):
        """
        Save an activity.

        Args:
            activity_tuple (tuple): Tuple with activity values.

        Returns:
            tuple: Tuple representing the saved activity.
        """
        activity = helpers.dbus_to_hamster_activity(activity_tuple)
        result = self._controller.activities.save(activity)

        # [FIXME]
        # self.activities_changed()
        return helpers.hamster_to_dbus_activity(result)

    @dbus.service.method(DBUS_ACTIVITIES_INTERFACE, in_signature='i')
    def Remove(self, pk):  # NOQA
        """Remove an activity.

        Args:
            pk (int): PK of the activity to be removed.

        Returns:
            None: Nothing.
        """
        activity = self._controller.activities.get(pk)
        self._controller.activities.remove(activity)

        # [FIXME]
        # self.activities_changed()
        return None

    @dbus.service.method(DBUS_ACTIVITIES_INTERFACE, in_signature='i', out_signature='(is(is)b)')
    def Get(self, pk):  # NOQA
        """
        Retrieve an ``hamster_lib.Activity`` based on it's PK.

        Args:
            pk (int): PK of the activity to be fetched.

        Returns:
            tuple: hamster_lib.Activity tuple
        """
        activity = self._controller.store.activities.get(pk)
        return helpers.hamster_to_dbus_activity(activity)

    @dbus.service.method(DBUS_ACTIVITIES_INTERFACE, in_signature='i',
        out_signature='a(is(is)b)')  # NOQA
    def GetAll(self, category_pk):
        """
        Retrieve all ``hamster_lib.Activity`` instances that match the criteria.

        Args:
            category_pk (int): hamster_lib.Category pk. Use ``-1`` for ``None`` and ``-2`` for
                ``False``. Refer to ``hamster_lib.storage.hamster_lib.ActivityManager.get_all``
                for details.

        Returns:
            tuple: (activity_tuple, error).
        """
        if category_pk == -1:
            category = None
        elif category_pk == -2:
            category = False
        else:
            category = self._controller.store.categories.get(category_pk)

        activities = self._controller.store.activities.get_all(category)

        return [helpers.hamster_to_dbus_activity(activity) for activity in activities]


class FactManager(dbus.service.Object):
    """FactManager object to be exposed via DBus."""

    def __init__(self, controller):
        """Initialize fact manager object."""
        self._controller = controller

        super(FactManager, self).__init__(
            bus_name=_get_dbus_bus_name(),
            object_path='/org/projecthamster/HamsterDBus/FactManager',
        )

    @dbus.service.method(DBUS_FACTS_INTERFACE, in_signature='s',
        out_signature='(isss(is(is)b)a(is))')  # NOQA
    def SaveRaw(self, raw_fact):
        """
        Take a raw_fact save it to our backend.

        Args:
            raw_fact (str): ``raw fact`` string.

        Returns:
            tuple (DBushamster_lib.Fact): Serialized version of the saved ``hamster_lib.Fact``
            instance.

        Note: This method is identical to ``Savehamster_lib.Fact`` with the only difference being
            that it takes a ``raw fact`` instead of a serialized ``hamster_lib.Fact`` instance.
        """
        fact = hamster_lib.Fact.create_from_raw_fact(raw_fact)
        result = self._controller.store.facts.save(fact)

        # [FIXME]
        # self.facts_changed()

        return helpers.hamster_to_dbus_fact(result)

    @dbus.service.method(DBUS_FACTS_INTERFACE, in_signature='(isss(is(is)b)a(is))',
        out_signature='(isss(is(is)b)a(is))')  # NOQA
    def Save(self, fact_tuple):
        """
        Take a fact save it to our backend.

        Args:
            fact_tuple (DBushamster_lib.Fact): ``hamster_lib.Fact`` to be saved.

        Returns:
            tuple (DBusFact): Serialized version of the saved ``hamster_lib.Fact``
                instance.
        """
        fact = helpers.dbus_to_hamster_fact(fact_tuple)
        result = self._controller.store.facts.save(fact)

        # [FIXME]
        # self.facts_changed()

        return helpers.hamster_to_dbus_fact(result)

    @dbus.service.method(DBUS_FACTS_INTERFACE, in_signature='i')
    def Remove(self, fact_pk):  # NOQA
        """
        Remove fact from storage by it's PK.

        Args:
            fact_pk (int): PK of the fact to be removed.

        Returns:
            None: Nothing.
        """
        fact = self._controller.store.facts.get(fact_pk)
        self._controller.store.facts.remove(fact)
        fact = self._controller.store.facts.get(fact_pk)

        # [FIXME]
        # if result:
        #    self.facts_changed()
        return None

    @dbus.service.method(DBUS_FACTS_INTERFACE, in_signature='i',
        out_signature='(isss(is(is)b)a(is))')  # NOQA
    def Get(self, fact_pk):
        """Get fact by PK.

        Args:
            fact_pk (int): PK of the fact to be retrieved.

        Returns:
            DBushamster_lib.Fact: Serialized ``hamster_lib.Fact`` instance.
        """
        fact = self._controller.facts.get(fact_pk)
        return helpers.hamster_to_dbus_fact(fact)

    @dbus.service.method(DBUS_FACTS_INTERFACE, in_signature='sss',
        out_signature='a(isss(is(is)b)a(is))')  # NOQA
    def GetAll(self, start, end, filter_term):
        """
        Get all facts matching criteria.

        Args:
            start (int): Unix-timestamp for start of timeframe. ``-1`` for ``None``.
            end (int): Unix-timestamp for end of timeframe. ``-1`` for ``None``.
            filter_term (str): Only consider ``hamster_lib.Facts`` with this string as part of
                their associated ``hamster_lib.Activity.name``

        Returns:
            list: A list of ``helpers.DBushamster_lib.Fact``-tuples.
                For details on those, please see ``helpers.hamster_to_dbus_fact``.

        Note:
            Our ``hamsterlib`` manager method is actually more flexible and would allow
            for ``datetime.datetime`` or ``datetime.time`` instances instead of just
            ``datetime.date`` instances for ``start`` and ``end``. But for compatibility
            reasons we stick with the simpler legacy version for now.
        """
        def get_start(start):
            return None

        def get_end(end):
            return None

        def get_filter_term(end):
            return filter_term

        facts = self._controller.store.facts.get_all(get_start(start), get_end(end),
            get_filter_term(filter_term))
        return [helpers.hamster_to_dbus_fact(fact) for fact in facts]

    @dbus.service.method(DBUS_FACTS_INTERFACE, out_signature='a(isss(is(is)b)a(is))')
    def GetTodays(self):  # NOQA
        """
        Get facts of today, respecting hamster day_start, day_end settings.

        Returns:
            list: A list of ``helpers.DBushamster_lib.Fact``-tuples.
                For details on those, please see ``helpers.DBushamster_lib.Fact``.

        Note:
            This only returns proper facts and will not include any ongoing fact!
        """
        facts = self.controller.store.facts.get_today()
        return [helpers.dbus_to_hamster_fact(fact) for fact in facts]
