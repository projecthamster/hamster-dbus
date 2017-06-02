# -*- encoding: utf-8 -*-

"""Unittests for our helpers module."""

from __future__ import absolute_import, unicode_literals

import datetime as dt

import dbus
import pytest
from hamster_lib import Activity, Category, Fact, Tag

from hamster_dbus import helpers
from hamster_dbus.helpers import DBusActivity, DBusCategory, DBusFact, DBusTag


@pytest.mark.parametrize(('value, expectation'), ((None, -1), (1, 1), ('1', 1)))
def test__none_to_int(value, expectation):
    """
    Make sure ``None`` is converted to an integer representation.

    All other values should be returned as unmodified integers.
    """
    result = helpers._none_to_int(value)
    assert result == expectation


@pytest.mark.parametrize(('value, expectation'), ((-1, None), (1, 1), ('1', 1)))
def test__int_to_none(value, expectation):
    """
    Make sure integer designating ``None`` gets converted properly.

    All other values should be returned as unmodified integers.
    """
    result = helpers._int_to_none(value)
    assert result == expectation


@pytest.mark.parametrize(('value', 'expectation'), (
    (dt.datetime(2017, 1, 1, 18, 50, 3), '2017-01-01 18:50:03'),
    (dt.date(2017, 12, 1), '2017-12-01'),
    (dt.time(18, 2, 1), '18:02:01'),
    (None, ''),
))
def test_datetime_to_text(value, expectation):
    """Make sure ``datetime`` instances are converted as expected."""
    result = helpers.datetime_to_text(value)
    assert result == expectation


@pytest.mark.parametrize(('value', 'expectation'), (
    ('2017-01-01 18:50:03', dt.datetime(2017, 1, 1, 18, 50, 3)),
    ('2017-12-01', dt.date(2017, 12, 1)),
    ('18:02:01', dt.time(18, 2, 1)),
    ('', None),
))
def test_text_to_datetime(value, expectation):
    """Make sure text representing``datetime`` instances is converted as expected."""
    result = helpers.text_to_datetime(value)
    assert result == expectation


def test_datetime_to_text_non_datetime():
    """Make sure an error is thrown if we pass invalid instances."""
    with pytest.raises(TypeError):
        helpers.datetime_to_text('foobar')


@pytest.mark.parametrize(('category', 'expectation'), (
    (Category('foo', 1), helpers.DBusCategory(1, 'foo')),
    (Category('foo', None), helpers.DBusCategory(-1, 'foo')),
    (None, helpers.DBusCategory(-2, '')),
))
def test_hamster_to_dbus_category(category, expectation):
    """Make sure that serialization works as intended."""
    result = helpers.hamster_to_dbus_category(category)
    assert result == expectation
    assert isinstance(result, DBusCategory)


@pytest.mark.parametrize(('category_tuple', 'expectation'), (
    ((1, 'foo'), Category('foo', 1)),
    ((-1, 'foo'), Category('foo', None)),
    ((-2, ''), None),
    (helpers.DBusCategory(1, 'foo'), Category('foo', 1)),
    (helpers.DBusCategory(-1, 'foo'), Category('foo', None)),
    (helpers.DBusCategory(-2, ''), None),
))
def test_dbus_to_hamster_category(category_tuple, expectation):
    """Make sure that de-serialization works as intended."""
    result = helpers.dbus_to_hamster_category(category_tuple)
    assert result == expectation
    if expectation:
        assert isinstance(result, Category)


@pytest.mark.parametrize(('activity', 'expectation'), (
    (Activity('foo', pk=1), DBusActivity(1, 'foo', DBusCategory(-2, ''), False)),
    (Activity('foo', pk=None), DBusActivity(-1, 'foo', DBusCategory(-2, ''), False)),
    (None, DBusActivity(-2, '', DBusCategory(-2, ''), False)),
))
def test_hamster_to_dbus_activity(activity, expectation):
    """Make sure that serialization works as intended."""
    result = helpers.hamster_to_dbus_activity(activity)
    assert result == expectation
    assert isinstance(result, DBusActivity)


@pytest.mark.parametrize(('activity_tuple', 'expectation'), (
    (DBusActivity(1, 'foo', DBusCategory(1, 'bar'), False),
     Activity('foo', 1, Category('bar', 1))),
    (DBusActivity(1, 'foo', DBusCategory(-2, ''), False), Activity('foo', 1)),
    (DBusActivity(-2, 'foo', DBusCategory(-2, ''), False), None),
))
def test_dbus_to_hamster_activity(activity_tuple, expectation):
    """Make sure that de-serialization works as intended."""
    result = helpers.dbus_to_hamster_activity(activity_tuple)
    assert result == expectation
    if expectation:
        assert isinstance(result, Activity)


@pytest.mark.parametrize(('tag', 'expectation'), (
    (Tag('foo', 1), helpers.DBusTag(1, 'foo')),
    (Tag('foo', None), helpers.DBusTag(-1, 'foo')),
    (None, helpers.DBusTag(-2, '')),
))
def test_hamster_to_dbus_tag(tag, expectation):
    """Make sure that serialization works as intended."""
    result = helpers.hamster_to_dbus_tag(tag)
    assert result == expectation
    assert isinstance(result, DBusTag)


@pytest.mark.parametrize(('tag_tuple', 'expectation'), (
    ((1, 'foo'), Tag('foo', 1)),
    ((-1, 'foo'), Tag('foo', None)),
    ((-2, ''), None),
    (helpers.DBusTag(1, 'foo'), Tag('foo', 1)),
    (helpers.DBusTag(-1, 'foo'), Tag('foo', None)),
    (helpers.DBusTag(-2, ''), None),
))
def test_dbus_to_hamster_tag(tag_tuple, expectation):
    """Make sure that de-serialization works as intended."""
    result = helpers.dbus_to_hamster_tag(tag_tuple)
    assert result == expectation
    if expectation:
        assert isinstance(result, Tag)


@pytest.mark.parametrize(('fact', 'expectation'), (
    (Fact(Activity('foo', pk=1), dt.datetime(2017, 2, 1, 18), pk=1),
     DBusFact(1, '2017-02-01 18:00:00', '', '',
        DBusActivity(1, 'foo', DBusCategory(-2, ''), False),
        dbus.Array([], '(is)'))),
    (Fact(Activity('foo', pk=1), dt.datetime(2017, 2, 1, 18), pk=None),
     DBusFact(-1, '2017-02-01 18:00:00', '', '',
        DBusActivity(1, 'foo', DBusCategory(-2, ''), False),
        dbus.Array([], '(is)'))),
    (Fact(Activity('foo', pk=1), start=None, pk=None),
     DBusFact(-1, '', '', '',
        DBusActivity(1, 'foo', DBusCategory(-2, ''), False),
        dbus.Array([], '(is)'))),
))
def test_hamster_to_dbus_fact(fact, expectation):
    """Make sure that serialization works as intended."""
    result = helpers.hamster_to_dbus_fact(fact)
    assert result == expectation
    assert isinstance(result, DBusFact)


@pytest.mark.parametrize(('fact_tuple', 'expectation'), (
    (DBusFact(-1, '2017-02-01 18:00:00', '', '',
        DBusActivity(1, 'foo', DBusCategory(-2, ''), False),
        dbus.Array([], '(is)')),
    Fact(Activity('foo', pk=1), dt.datetime(2017, 2, 1, 18), pk=None)),
    (DBusFact(1, '2017-02-01 18:00:00', '', '',
        DBusActivity(1, 'foo', DBusCategory(-2, ''), False),
        dbus.Array([], '(is)')),
    Fact(Activity('foo', pk=1), dt.datetime(2017, 2, 1, 18), pk=1)),
))
def test_dbus_to_hamster_fact(fact_tuple, expectation):
    """Make sure that de-serialization works as intended."""
    result = helpers.dbus_to_hamster_fact(fact_tuple)
    assert result == expectation
    assert isinstance(result, Fact)
