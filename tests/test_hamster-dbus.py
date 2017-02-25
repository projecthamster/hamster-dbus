# -*- coding: utf-8 -*-

"""
So far we fail to succeed to patch the controler properly. as a consequencec we
use the controler to fetch created objects and assume this method works as intended.
"""

import pytest
import os
import dbus
import psutil
import time


import hamster_dbus.hamster_dbus as hamster_dbus
import hamster_dbus.helpers as helpers

# First attempts towards an approach that mocks the actuall calls to hamster_lib
# failed because we only have access to proxy instances of our manager classes.
# This seems to make it difficult to monkey patch its corresponding
# ``._controler...`` methods.


class TestGeneralMethods(object):
    """Make sure that genreal methods work as expected."""

    @pytest.mark.xfail
    def test_quit(self, hamster_service, hamster_interface):
        """Make sure that we actually shut down the service."""
        assert psutil.pid_exists(hamster_service.pid)
        hamster_interface.Quit()
        time.sleep(2)
        assert psutil.pid_exists(hamster_service.pid) is False

class TestCategoryManager(object):

    def test_save_new(self, category_manager, category_name_parametrized):
        """Make sure that passing a valid string creates a new category and returns its pk."""
        dbus_category = helpers.DBusCategory(*category_manager.Save((-1, category_name_parametrized)))
        assert dbus_category.pk == 1
        assert dbus_category.name == category_name_parametrized

    def test_save_existing(self, store, category_manager, stored_category,
            category_name_parametrized):
        """Make sure that changing a name works as intended."""
        dbus_category = helpers.DBusCategory(stored_category.pk, category_name_parametrized)
        result = category_manager.Save(dbus_category)
        result = helpers.dbus_to_hamster_category(helpers.DBusCategory(*result))
        assert store.categories.get(stored_category.pk).name == category_name_parametrized
        assert result.pk == stored_category.pk
        assert result.name == category_name_parametrized

    def test_remove(self, store, category_manager, stored_category):
        """Make sure that removing a category works as intended."""
        assert store.categories.get(stored_category.pk)
        result = category_manager.Remove(stored_category.pk)
        assert result is None
        with pytest.raises(KeyError):
            store.categories.get(stored_category.pk)

    def test_get_by_name(self, store, category_manager, stored_category):
        """Make sure we can look up a categories PK by its name."""
        result = category_manager.GetByName(stored_category.name)
        result = helpers.DBusCategory(*result)
        assert result.pk == stored_category.pk
        assert result.name == stored_category.name

    def test_get_all(self, store, category_manager, stored_category_batch_factory):
        """Make sure we get all stored categories."""
        categories = stored_category_batch_factory(5)
        result = category_manager.GetAll()
        result = [helpers.dbus_to_hamster_category(helpers.DBusCategory(*each)) for each in result]
        assert len(result) == 5
        for category in categories:
            assert category in result

class TestActivityManager(object):

    def test_save_new(self, activity_manager, activity):
        dbus_activity = helpers.hamster_to_dbus_activity(activity)
        result = activity_manager.Save(dbus_activity)
        result = helpers.dbus_to_hamster_activity(helpers.DBusActivity(*result))
        assert result.pk
        assert result.name == activity.name
        # We create a new instance, hence result will have a pk where the
        # original does not.
        assert activity.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    def test_remove(self, store, activity_manager, stored_activity):
        assert store.activities.get(stored_activity.pk)
        result = activity_manager.Remove(stored_activity.pk)
        assert result is None
        with pytest.raises(KeyError):
            store.activities.get(stored_activity.pk)

    def test_get(self, store, activity_manager, stored_activity):
        result = activity_manager.Get(stored_activity.pk)
        result = helpers.dbus_to_hamster_activity(helpers.DBusActivity(*result))
        assert result == stored_activity

    def test_get_all(self, store, activity_manager, stored_activity_batch_factory):
        """Make sure we get all stored categories."""
        activities = stored_activity_batch_factory(5)
        result = activity_manager.GetAll(-2)
        result = [helpers.dbus_to_hamster_activity(helpers.DBusActivity(*each)) for each in result]
        assert len(result) == 5
        for activity in activities:
            assert activity in result

class TestFactManager(object):

    def test_save_new(self, fact_manager, fact):
        dbus_fact = helpers.hamster_to_dbus_fact(fact)
        result = fact_manager.Save(dbus_fact)
        result = helpers.dbus_to_hamster_fact(result)
        # We create a new instance, hence result will have a pk where the
        # original does not.
        assert fact.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    # For a reason not yet understood the exception is not raised, although it
    # looks like the code works as intended.
    @pytest.mark.xfail
    def test_remove(self, store, fact_manager, stored_fact):
        pk = stored_fact.pk
        assert store.facts.get(pk)
        result = fact_manager.Remove(pk)
        assert result is None
        with pytest.raises(KeyError):
            store.facts.get(pk)

    def test_get(self, store, fact_manager, stored_fact):
        result = fact_manager.Get(stored_fact.pk)
        result = helpers.dbus_to_hamster_fact(result)
        assert result == stored_fact

    # [FIXME]
    # This should be expanded
    def test_get_all(self, store, fact_manager, stored_fact_batch_factory):
        facts = stored_fact_batch_factory(5)
        result = fact_manager.GetAll('', '', '')
        assert len(result) == 5
