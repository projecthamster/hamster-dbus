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
# Currently hamster-lib objects need to be converted into something that can be
# passed over dbus. Future iteration should revisit this and see if we can
# expose those objects as dbus objects and consequently just pass those.

# If the ``dbus.service.method`` decorator spans multiple lines we need to add
# the ``   # NOQA`` afterwards instead of the actual function definition.
from __future__ import absolute_import, unicode_literals

import dbus
import dbus.service
import hamster_lib

from hamster_dbus import helpers

DBUS_CATEGORIES_INTERFACE = 'org.projecthamster.HamsterDBus.CategoryManager1'
DBUS_TAGS_INTERFACE = 'org.projecthamster.HamsterDBus.TagManager1'
DBUS_ACTIVITIES_INTERFACE = 'org.projecthamster.HamsterDBus.ActivityManager1'
DBUS_FACTS_INTERFACE = 'org.projecthamster.HamsterDBus.FactManager1'


def _get_dbus_bus_name(bus=None):
    """Return the bus name."""
    # We wrap this in a function instead of a constant to avoid instant
    # instantiation if we use this module as a library.
    if not bus:
        bus = dbus.SessionBus()
    return dbus.service.BusName(
        name='org.projecthamster.HamsterDBus',
        bus=bus
    )


class HamsterDBus(dbus.service.Object):
    """A dbus object providing access to general hamster-lib capabilities."""

    def __init__(self, loop):
        """Initialize main DBus object."""
        self._loop = loop

        super(HamsterDBus, self).__init__(
            bus_name=_get_dbus_bus_name(),
            object_path='/org/projecthamster/HamsterDBus',
        )

    @dbus.service.signal('org.projecthamster.HamsterDBus1')
    def CategoryChanged(self):  # NOQA
        """Signal indicating that at least one category may have been modified."""
        pass

    @dbus.service.signal('org.projecthamster.HamsterDBus1')
    def ActivityChanged(self):  # NOQA
        """Signal indicating that at least one activity may have been modified."""
        pass

    @dbus.service.signal('org.projecthamster.HamsterDBus1')
    def TagChanged(self):  # NOQA
        """Signal indicating that at least one tag may have been modified."""
        pass

    @dbus.service.signal('org.projecthamster.HamsterDBus1')
    def FactChanged(self):  # NOQA
        """Signal indicating that at least one fact may have been modified."""
        pass

    @dbus.service.method('org.projecthamster.HamsterDBus1')
    def Quit(self):  # NOQA
        """Shutdown the service."""
        self._loop.quit()


class CategoryManager(dbus.service.Object):
    """CategoryManager object to be exposed via DBus."""

    def __init__(self, controller, main_object, bus=None):
        """
        Initialize category manager object.

        Args:
            controller: FIXME
            main_object: ``HamsterDBus`` object. This is needed in order to
                emmit signals.
            bus (optional): FIXME
        """
        self._controller = controller
        self._main_object = main_object
        self._busname = _get_dbus_bus_name(bus)

        super(CategoryManager, self).__init__(
            bus_name=self._busname,
            object_path='/org/projecthamster/HamsterDBus/CategoryManager',
        )

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

        self._main_object.CategoryChanged()
        return helpers.hamster_to_dbus_category(category)

    @dbus.service.method(DBUS_CATEGORIES_INTERFACE, in_signature='(is)', out_signature='(is)')
    def GetOrCreate(self, category_tuple):  # NOQA
        """
        For details please refer to ``hamster_lib.storage``.

        Args:
            category (helpers.DBusCategory or None): The category 'dbus encoded'.

        Returns:
            helpers.DBusCategory or None: The retrieved or created category.
                Either way, the returned Category will contain all data from
                the backend, including its primary key.
        """
        category = helpers.dbus_to_hamster_category(category_tuple)
        category = self._controller.store.categories.get_or_create(category)

        self._main_object.CategoryChanged()
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

        self._main_object.CategoryChanged()
        return None

    @dbus.service.method(DBUS_CATEGORIES_INTERFACE, in_signature='i', out_signature='(is)')
    def Get(self, pk):  # NOQA
        """
        Return a category based on their pk.

        Args:
            pk (int): PK of the category to be retrieved.

        Returns:
            tuple: helpers.DBusCategory tuple.

        Raises:
            KeyError: If no such PK was found.
        """
        category = self._controller.categories.get(pk)
        return helpers.hamster_to_dbus_category(category)

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


class TagManager(dbus.service.Object):
    """TagManager object to be exposed via DBus."""

    def __init__(self, controller, main_object, bus=None):
        """
        Initialize tag manager object.

        Args:
            controler: FIXME
            main_object: ``HamsterDBus`` object. This is needed in order to
                emmit signals.
            bus (optional): FIXME
        """
        self._controller = controller
        self._main_object = main_object
        self._busname = _get_dbus_bus_name(bus)

        super(TagManager, self).__init__(
            bus_name=_get_dbus_bus_name(),
            object_path='/org/projecthamster/HamsterDBus/TagManager',
        )

    @dbus.service.method(DBUS_TAGS_INTERFACE, in_signature='(is)', out_signature='(is)')
    def Save(self, tag_tuple):  # NOQA
        """
        Save tag.

        Args:
            tag_tuple: hamster_lib.Tag tuple.

        Returns:
            helpers.DBusTag: For details please see ``helpers.haster_to_dbus_tag``.
        """
        tag = helpers.dbus_to_hamster_tag(tag_tuple)
        tag = self._controller.store.tags.save(tag)

        self._main_object.TagChanged()
        return helpers.hamster_to_dbus_tag(tag)

    @dbus.service.method(DBUS_TAGS_INTERFACE, in_signature='i')
    def Remove(self, pk):  # NOQA
        """
        Remove a tag.

        Args:
            pk (int): PK of the tag to be removed.

        Returns:
            None: Nothing.
        """
        # [TODO]
        # Once LIB-239 has been solved, we should be able to skip extra tag
        # retrieval.
        tag = self._controller.store.tags.get(pk)
        self._controller.store.tags.remove(tag)

        self._main_object.TagChanged()
        return None

    @dbus.service.method(DBUS_TAGS_INTERFACE, in_signature='s', out_signature='(is)')
    def GetByName(self, name):  # NOQA
        """
        Look up a tag by its name and return its PK.

        Args:
            name (str): Name of the tag to we want the PK of.

        Returns:
            helpers.DBusTag: For details please see ``helpers.haster_to_dbus_tag``.
        """
        tag = self._controller.store.tags.get_by_name(name)
        return helpers.hamster_to_dbus_tag(tag)

    @dbus.service.method(DBUS_TAGS_INTERFACE, out_signature='a(is)')
    def GetAll(self):  # NOQA
        """
        Get all tags.

        Returns:
            list: List of ``helpers.DBusTag``s. For details see
                ``helpers.hamster_to_dbus_tag``.
        """
        tags = self._controller.store.tags.get_all()
        return [helpers.hamster_to_dbus_tag(tag) for tag in tags]


class ActivityManager(dbus.service.Object):
    """ActivityManager object to be exposed via DBus."""

    def __init__(self, controller, main_object):
        """
        Initialize activity manager object.

        Args:
            controler: FIXME
            main_object: ``HamsterDBus`` object. This is needed in order to
                emmit signals.
        """
        # [FIXME]
        # Unlike with ``CategoryManager`` and ``TagManager`` we do not allow for
        # a custom bus.
        self._controller = controller
        self._main_object = main_object

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

        self._main_object.ActivityChanged()
        self._main_object.CategoryChanged()
        # This is because during activity creation/updating a new category may
        # be created as well.
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

        self._main_object.ActivityChanged()
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

    def __init__(self, controller, main_object):
        """
        Initialize fact manager object.

        Args:
            controler: FIXME
            main_object: ``HamsterDBus`` object. This is needed in order to
                emmit signals.
        """
        # [FIXME]
        # Unlike with ``CategoryManager`` and ``TagManager`` we do not allow for
        # a custom bus.
        self._controller = controller
        self._main_object = main_object

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

        self._main_object.FactChanged()
        self._main_object.CategoryChanged()
        self._main_object.TagChanged()
        self._main_object.ActivityChanged()
        # This is because during creation/updating a new related instances
        # may be created as well.

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

        self._main_object.FactChanged()
        self._main_object.CategoryChanged()
        self._main_object.TagChanged()
        self._main_object.ActivityChanged()
        # This is because during creation/updating a new related instances
        # may be created as well.

        return helpers.hamster_to_dbus_fact(result)

    @dbus.service.method(DBUS_FACTS_INTERFACE, in_signature='i')
    def Remove(self, pk):  # NOQA
        """
        Remove fact from storage by it's PK.

        Args:
            fact_pk (int): PK of the fact to be removed.

        Returns:
            None: Nothing.
        """
        fact = self._controller.store.facts.get(pk)
        self._controller.store.facts.remove(fact)

        self._main_object.FactChanged()
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
