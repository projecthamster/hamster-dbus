
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

from collections import namedtuple

DBusFact = namedtuple('DBusFact', ('pk', 'start', 'end', 'description', 'activity_name',
    'activity_pk', 'category_name', 'tags', 'date', 'delta'))



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

def _represent_category(category, legacy_mode=False):
        """
        Return a string representation of a retrieved category that can be returned via dbus.

        Args:
            category (hamsterlib.Category): Category instance or None.
            fallback (str): String to represent ``category=None``.

        Returns:
            str: Name of the passed ``Category`` or ``empty_string`` to indicate
                that ``category=None``.

        Quite often we will end up with a situation where we need to check whether a
        category is ``None`` or is a proper instance with a name. In order to avoid
        code duplication this is done once in this function.
        Because the representation logic is specific to our dbus requirements we
        do not simply adjust ``hamsterlib.Category.__str__``.

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


def _hamster_to_dbus_fact(self, fact):
    """
    Perform the conversion between Fact-instance and dbus supported data types.

    As far as we can tell of now a dbus-fact looks has the signature
    of 'iiissisasii' with:
            i  pk
            i  start_time
            i  end_time
            s  description
            s  activity name
            i  activity pk
            s  category name
            as List of fact tags
            i  date (timestamp?)
            i  delta (format?)
    """

    # Convert our proper datatypes into something dbus can handle.
    if fact.end:
        end = timegm(fact.end.timetuple())
    else:
        end = 0

    if fact.description:
        description = fact.description
    else:
        description = ''

    if fact.activity.category:
        category_name = fact.activity.category.name
    else:
        category_name = _get_unsorted_localized()

    if fact.delta:
        delta = fact.delta.total_second()
    else:
        delta = 0

    return DBusFact(
        pk=fact.id,
        start=timegm(fact.start.timetuple()),
        end=end,
        description=description,
        activity_name=fact.activity.name,
        activity_pk=fact.activity.pk,
        category_name=category_name,
        # placeholer for tags
        tags=dbus.Array(['foo', 'bar'], signature='s'),
        date=date,
        delta=delta
    )


def _get_unsorted_localized():
    return 'unsorted localized'
