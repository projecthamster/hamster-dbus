
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
# along with 'hamster-dbus'.  If not, see <http://www.gnu.org/licenses/>.

import datetime
from collections import namedtuple

import hamster_lib

DBusCategory = namedtuple('DBusCategory', ('pk', 'name'))
# 'category' is supposed to store an ``DBushamster_lib.Category`` instance.
DBusActivity = namedtuple('DBusActivity', ('pk', 'name', 'category', 'deleted'))
# 'activity' is supposed to store an ``DBushamster_lib.Activity`` instance.
DBusFact = namedtuple('DBusFact', ('pk', 'start', 'end', 'description', 'activity', 'tags'))

def _none_to_int(value):
    if value is None:
        value = -1
    return value


def _int_to_none(value):
    if value == -1:
        value = None
    return value


def get_config():
    """Get config to be passed to controler."""
    return {
        'store': 'sqlalchemy',
        'day_start': datetime.time(5, 30, 0),
        'fact_min_delta': 60,
        'tmpfile_path': '/tmp/tmpfile.pickle',
        'db_engine': 'sqlite',
        'db_path': ':memory:',
    }

def _represent_category(category, legacy_mode=False):
        """
        Return a string representation of a retrieved category that can be returned via dbus.

        Args:
            category (hamsterlib.hamster_lib.Category): hamster_lib.Category instance or None.
            fallback (str): String to represent ``category=None``.

        Returns:
            str: Name of the passed ``hamster_lib.Category`` or ``empty_string`` to indicate
                that ``category=None``.

        Quite often we will end up with a situation where we need to check whether a
        category is ``None`` or is a proper instance with a name. In order to avoid
        code duplication this is done once in this function.
        Because the representation logic is specific to our dbus requirements we
        do not simply adjust ``hamsterlib.hamster_lib.Category.__str__``.

        Legacy hamster does this on the db level by using ``coalesce`` to assign
        fallback value (``unsorted_localized``). As we opt to leave handling
        null-categories to the client as its sees fit we need a way to indicate
        that there is no category name because there is no category. This is
        done by returning an empty string. However, in order to stay backwards
        compatible, it is possible to provide a custom fallback (such as legacycy
        ``unsorted_localized`` in order to handle represenation of ``None``
        categories by ``dbus-hamster``.
        """

        if category:
            result = category.name
        else:
            if legacy_mode:
                result = 'unsorted category'
            else:
                result = ''
        return result



# This is needed because not all types used in ``as_tuple`` can be passed
# through dbus
def hamster_to_dbus_category(category):
    def get_pk(category):
        return _none_to_int(category.pk)

    def get_name(category):
        return category.name

    return DBusCategory(
        pk=get_pk(category),
        name=get_name(category)
    )


def dbus_to_hamster_category(category_tuple):
    def get_pk(category_tuple):
        pk = category_tuple.pk
        return _int_to_none(pk)

    def get_name(category_tuple):
        return category_tuple.name

    category_tuple = DBusCategory(*category_tuple)
    return hamster_lib.Category(
        pk=get_pk(category_tuple),
        name=get_name(category_tuple)
    )


def hamster_to_dbus_activity(activity):
    # (activity.pk, activity.name, (category.pk, category.name),
    # activity.deleted)
    # If activity.category=None we need to encode this information in a way that
    # accomodates dbus type constrains. We can not simply pass None. In order to
    # distinguish this case from categories that have just not yet recieved a pk
    # we use ``-2``.
    def get_pk(activity):
        pk = activity.pk
        return _none_to_int(pk)

    def get_name(activity):
        return activity.name

    def get_category(activity):
        if activity is None:
            category = (-2, '')
        else:
            category = hamster_to_dbus_category(activity.category)
        return category

    def get_deleted(activity):
        return activity.deleted

    return DBusActivity(
        pk=get_pk(activity),
        name=get_name(activity),
        category=get_category(activity),
        deleted=get_deleted(activity)
    )


def dbus_to_hamster_activity(activity_tuple):
    """
    Convert an 'DBus activity tuple to activity.

    Returns:
        hamster_lib.Activity: hamster_lib.Activity instance.
    """
    def get_pk(activity_tuple):
        return _int_to_none(activity_tuple.pk)

    def get_name(activity_tuple):
        return activity_tuple.name

    def get_category(activity_tuple):
        category_tuple = activity_tuple.category
        return dbus_to_hamster_category(category_tuple)

    activity_tuple = DBusActivity(*activity_tuple)

    return hamster_lib.Activity(
        pk=get_pk(activity_tuple),
        name=get_name(activity_tuple),
        category=get_category(activity_tuple),
    )

# Note that we currently do not support passing timezone information!
def hamster_to_dbus_fact(fact):
    """
    Perform the conversion between hamster_lib.Fact-instance and dbus supported data types.

    (iiis(is(is)b)a(is))':
    i           pk: -1 -> None
    s           start
    s           end
    s           description
    (is(is)b)   activity tuple: (pk, name, category_tuple).
    a(is)       list of tag tuples: (pk, name). pk=-1 -> None
    """

    def get_pk(fact):
        return _none_to_int(fact.pk)

    def get_start(fact):
        if fact.start:
            start = fact.start.strftime('%Y-%m-%d %H:%M:%S')
        else:
            start = ''
        return start

    def get_end(fact):
        if fact.end:
            end = fact.end.strftime('%Y-%m-%d %H:%M:%S')
        else:
            end = ''
        return end

    def get_activity(fact):
        activity = fact.activity
        return hamster_to_dbus_activity(activity)

    def get_description(fact):
        return fact.description

    def get_tags(fact):
        # [FIXME]
        return []

    return DBusFact(
        pk=get_pk(fact),
        start=get_start(fact),
        end=get_end(fact),
        activity=get_activity(fact),
        # [FIXME]
        tags=get_tags(fact),
        description=get_description(fact),
    )


def dbus_to_hamster_fact(fact_tuple):
    def get_pk(fact_tuple):
        return _int_to_none(fact_tuple.pk)

    def get_start(fact_tuple):
        if fact_tuple.start:
            start = datetime.datetime.strptime(fact_tuple.start, '%Y-%m-%d %H:%M:%S')
        else:
            start = None
        return start

    def get_end(fact_tuple):
        if fact_tuple.end:
            end = datetime.datetime.strptime(fact_tuple.end, '%Y-%m-%d %H:%M:%S')
        else:
            end = None
        return end

    def get_activity(fact_tuple):
        return dbus_to_hamster_activity(fact_tuple.activity)

    def get_tags(fact_tuple):
        return []

    def get_description(fact_tuple):
        return fact_tuple.description

    # Make sure we can deal with proper DBusFact instances as well as with
    # 'unprepared' normal tuples.
    fact_tuple = DBusFact(*fact_tuple)
    return hamster_lib.Fact(
        pk=get_pk(fact_tuple),
        start=get_start(fact_tuple),
        end=get_end(fact_tuple),
        activity=get_activity(fact_tuple),
        tags=get_tags(fact_tuple),
        description=get_description(fact_tuple)
    )
