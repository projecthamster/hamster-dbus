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

"""
Helper functions to ease working with dbus objects and type conversion.

This is the central place were the dbus "signature" of our hamster_lib objects
is defined and documented. All dbus code is advised to use those serialization methods to
ensure consistend representation.
"""

import datetime
from collections import namedtuple

import dbus
import hamster_lib
from six import text_type

DBusCategory = namedtuple('DBusCategory', ('pk', 'name'))
# 'category' is supposed to store an ``DBushamster_lib.Category`` instance.
DBusActivity = namedtuple('DBusActivity', ('pk', 'name', 'category', 'deleted'))
DBusTag = namedtuple('DBusTag', ('pk', 'name'))
# 'activity' is supposed to store an ``DBushamster_lib.Activity`` instance.
DBusFact = namedtuple('DBusFact', ('pk', 'start', 'end', 'description', 'activity', 'tags'))


def _none_to_int(value):
    """
    Serialize ``None`` as an integer value.

    Args:
        value (int, None): Value to 'sanitize'.

    Returns:
        int: Return ``-1`` if ``value=None`` else the original value.
    """
    if value is None:
        value = -1
    return int(value)


def _int_to_none(value):
    """
    Convert integer representation of ``None`` to the proper python type.

    Args:
        value (int): Value to convert to 'sanitize'.

    Return:
        int or None: The original integer or ``None`` if ``value=-1``.
    """
    value = int(value)
    if value == -1:
        value = None
    return value


def datetime_to_text(datetime_info):
    """
    Serialize ``datetime``, ``date`` or ``time`` instances as text.

    Args:
        datetime_info (dt.datetime, dt.date, dt.time, None): Python datetime
        information that is to be serialized.

    Returns:
        text_type: Returns optinionated text representation of passed datetime
        information. ``dt.datetime`` will be represented as ``%Y-%m-%d %H:%M:%S``,
        ``dt.date`` will be represented as ``%Y-%m-%d`` and ``dt.time`` as
        ``%H-%M-%S``. ``None`` will be serialized as an ``empty string``.

    Raises:
        TypeError: If ``datetime_info`` is not ``datetime.datetime``,
        ``datetime.date``, ``datetime.time`` or ``None``.
    """
    if isinstance(datetime_info, datetime.datetime):
        result = datetime_info.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(datetime_info, datetime.date):
        result = datetime_info.strftime('%Y-%m-%d')
    elif isinstance(datetime_info, datetime.time):
        result = datetime_info.strftime('%H:%M:%S')
    elif datetime_info is None:
        result = ''
    else:
        raise TypeError
    return text_type(result)


def text_to_datetime(datetime_text):
    """
    Serialize a text string to its corresponding python datetime instance.

    Args:
        datetime_text (text_type): Text to be converted. If not an
        ``empty string`` this needs to match one of the following formats:
        ``%Y-%m-%d %H:%M:%S``, ``%Y-%m-%d`` or ``%H:%M:%S``,

    Returns:
        datetime.datetime, datetime.date, datetime.time: A python instance
        mathing the supplied text or the ``empty string`` if
        ``datetime_text=None``.

    Raises:
        ValueError: If passed text does not match any of the given formats.

    """
    if datetime_text == '':
        result = None
    else:
        try:
            result = datetime.datetime.strptime(datetime_text, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                result = datetime.datetime.strptime(datetime_text, '%Y-%m-%d').date()
            except ValueError:
                result = datetime.datetime.strptime(datetime_text, '%H:%M:%S').time()
    return result


# This is needed because not all types used in ``as_tuple`` can be passed
# through dbus
def hamster_to_dbus_category(category):
    """
    Convert a ``hamster_lib.Category`` instance to its dbus representation.

    The resulting tuple is suitable for dbus messages and has the following
    signature: '(is)'.

    i = category.pk
    s = category.name

    Args:
        category (hamster_lib.Category): Category instance to be serialized.

    Returns:
        DBusCategory: Serialized category instance. If the category to be
        serialized does not yet have a PK the resulting tuple will have
        ``pk=-1``. If the category is actually ``None`` the resulting
        tuple will have ``pk=-2``.
    """
    def get_pk(category):
        return _none_to_int(category.pk)

    def get_name(category):
        return category.name

    if category is None:
        result = DBusCategory(-2, '')
    else:
        result = DBusCategory(
            pk=get_pk(category),
            name=get_name(category)
        )
    return result


def dbus_to_hamster_category(category_tuple):
    """
    Return a ``hamster_lib.Category`` from its passed DBus representation.

    Args:
        category_tuple (DBusCategory or tuple): Tuple to be serialized. If a
        non ``DBusCategory`` tuple is passed its values need to be ordered as
        for ``DBusCategory``.
        A ``category.pk`` of ``-1`` will be converted to ``None``.

    Returns:
        hamster_lib.Category or None: Category constructed from tuple data.
        If ``category_tuple.pk=-2`` ``None`` will be returned.
    """
    def get_pk(category_tuple):
        pk = category_tuple.pk
        return _int_to_none(pk)

    def get_name(category_tuple):
        return category_tuple.name

    category_tuple = DBusCategory(*category_tuple)

    if category_tuple.pk == -2:
        result = None
    else:
        result = hamster_lib.Category(
            pk=get_pk(category_tuple),
            name=get_name(category_tuple)
        )
    return result


def hamster_to_dbus_activity(activity):
    """
    Convert a ``hamster_lib.Activity`` instance to it's dbus representation.

    The resulting tuple is suitable for dbus messages and has the following
    signature: '(is(is))'. For details on category serialization see
    ``hamster_to_dbus_category``.

    i = activity.pk
    s = activity.name
    (is) = category tuple: (category.pk, category.name)

    Args:
        activity (hamster_lib.Activity): Activity instance to be serialized.

    Returns:
        DBusActivity: Serialized activity instance. If the activity to be
        serialized does not yet have a PK the resulting tuple will have
        ``pk=-1``. If the activity is actually ``None`` the resulting
        tuple will have ``pk=-2``.
    """
    def get_pk(activity):
        pk = activity.pk
        return _none_to_int(pk)

    def get_name(activity):
        return activity.name

    def get_category(activity):
        return hamster_to_dbus_category(activity.category)

    def get_deleted(activity):
        return activity.deleted

    if activity is None:
        result = DBusActivity(-2, '', DBusCategory(-2, ''), False)
    else:
        result = DBusActivity(
            pk=get_pk(activity),
            name=get_name(activity),
            category=get_category(activity),
            deleted=get_deleted(activity)
        )
    return result


def dbus_to_hamster_activity(activity_tuple):
    """
    Convert an 'DBus activity tuple to activity.

    Args:
        activity_tuple (DBusActivity or tuple): Tuple to be serialized. If a
        non ``DBusActivity`` tuple is passed its values need to be ordered as
        for ``DBusActivity``.
        An ``activity.pk`` of ``-1`` will be converted to ``None``.

    Returns:
        hamster_lib.Activity or None: hamster_lib.Activity instance. If
        ``activity_tuple.pk=-2`` ``None`` will be returned.
    """
    def get_pk(activity_tuple):
        return _int_to_none(activity_tuple.pk)

    def get_name(activity_tuple):
        return activity_tuple.name

    def get_category(activity_tuple):
        category_tuple = activity_tuple.category
        return dbus_to_hamster_category(category_tuple)

    activity_tuple = DBusActivity(*activity_tuple)

    if activity_tuple.pk == -2:
        result = None
    else:
        result = hamster_lib.Activity(
            pk=get_pk(activity_tuple),
            name=get_name(activity_tuple),
            category=get_category(activity_tuple),
        )
    return result


def hamster_to_dbus_tag(tag):
    """Convert a ``hamster_lib.Tag`` instance to its dbus representation.

    The resulting tuple is suitable for dbus messages and has the following
    signature: '(is)'.

    i = tag.pk
    s = tag.name

    Args:
        tag (hamster_lib.Tag): Tag instance to be serialized.

    Returns:
        DBusTag: Serialized tag instance. If the tag to be
        serialized does not yet have a PK the resulting tuple will have
        ``pk=-1``. If the tag is actually ``None`` the resulting
        tuple will have ``pk=-2``.
    """
    def get_pk(tag):
        return _none_to_int(tag.pk)

    def get_name(tag):
        return tag.name

    if tag is None:
        result = DBusTag(-2, '')
    else:
        result = DBusTag(
            pk=get_pk(tag),
            name=get_name(tag)
        )
    return result


def dbus_to_hamster_tag(tag_tuple):
    """Return a ``hamster_lib.Tag`` from its passed dbus representation.

    Args:
        tag_tuple (DBusTag or tuple): Tuple to be serialized. If a
        non ``DBusTag`` tuple is passed its values need to be ordered as
        for ``DBusTag``.
        A ``tag.pk`` of ``-1`` will be converted to ``None``.

    Returns:
        hamster_lib.Tag or None: Tag constructed from tuple data.
        If ``tag_tuple.pk=-2`` ``None`` will be returned.
    """
    def get_pk(tag_tuple):
        pk = tag_tuple.pk
        return _int_to_none(pk)

    def get_name(tag_tuple):
        return tag_tuple.name

    tag_tuple = DBusTag(*tag_tuple)

    if tag_tuple.pk == -2:
        result = None
    else:
        result = hamster_lib.Tag(
            pk=get_pk(tag_tuple),
            name=get_name(tag_tuple)
        )
    return result


# Note that we currently do not support passing timezone information!
def hamster_to_dbus_fact(fact):
    """
    Perform the conversion between hamster_lib.Factinstance and dbus supported data types.

    The resulting tuple is suitable for dbus messages and has the following
    signature: (isss(is(is)b)a(is))'

    i           pk
    s           start
    s           end
    s           description
    (is(is)b)   activity tuple: (pk, name, category_tuple)
    a(is)       list of tag tuples: (pk, name)

    Args:
        fact (hamster_lib.Fact): Fact instance to be serialized.

    Returns:
        DBusFact: Serialized fact instance. If the  fact to be
        serialized does not yet have a PK the resulting tuple will have
        ``pk=-1``. For details on the serialized activity refer to
        ``hamster_to_dbus_activity``.
    """
    def get_pk(fact):
        return _none_to_int(fact.pk)

    def get_start(fact):
        return datetime_to_text(fact.start)

    def get_end(fact):
        return datetime_to_text(fact.end)

    def get_activity(fact):
        activity = fact.activity
        return hamster_to_dbus_activity(activity)

    def get_description(fact):
        result = fact.description
        if fact.description is None:
            result = ''
        return result

    def get_tags(fact):
        # We need to build the Array explicitly in order to avoid python-dbus
        # trying to guess its signature (which fails for empty lists).
        return dbus.Array([hamster_to_dbus_tag(tag) for tag in fact.tags], '(is)')

    return DBusFact(
        pk=get_pk(fact),
        start=get_start(fact),
        end=get_end(fact),
        description=get_description(fact),
        activity=get_activity(fact),
        tags=get_tags(fact),
    )


def dbus_to_hamster_fact(fact_tuple):
    """
    Return a ``hamster_lib.Fact`` instance from its dbus representation.

    Args:
        fact_tuple (DBusFact or tuple): Tuple to be serialized. If a
        non ``DBusFact`` tuple is passed its values need to be ordered as
        for ``DBusFact``.
        A ``fact.pk`` of ``-1`` will be converted to ``None``.

    Returns:
        hamster_lib.Fact: Fact constructed from tuple data.
    """
    def get_pk(fact_tuple):
        return _int_to_none(fact_tuple.pk)

    def get_start(fact_tuple):
        return text_to_datetime(fact_tuple.start)

    def get_end(fact_tuple):
        return text_to_datetime(fact_tuple.end)

    def get_activity(fact_tuple):
        return dbus_to_hamster_activity(fact_tuple.activity)

    def get_tags(fact_tuple):
        return [dbus_to_hamster_tag(tag) for tag in fact_tuple.tags]

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
