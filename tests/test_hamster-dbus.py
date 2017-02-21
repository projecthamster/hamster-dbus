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


class TestGeneralMethods(object):
    """Make sure that genreal methods work as expected."""

    #@pytest.mark.xfail
    #def test_quit(self, hamster_service, hamster_interface):
    #    """Make sure that we actually shut down the service."""
    #    assert psutil.pid_exists(hamster_service.pid)
    #    hamster_interface.Quit()
    #    time.sleep(2)
    #    assert psutil.pid_exists(hamster_service.pid) is False

    def test_add_category_valid(self, mocker, controler, hamster_interface, category_name_parametrized):
        """Make sure that passing a valid string creates a new category and returns its pk."""
        name = category_name_parametrized
        result = hamster_interface.AddCategory(name)
        assert result >= 0
        assert controler.categories.get(result).name == name

    def test_update_category(self, store, hamster_interface, stored_category,
            category_name_parametrized):
        """Make sure that changing a name works as intended."""
        name = category_name_parametrized
        assert store.categories.get(stored_category.pk)
        result = hamster_interface.UpdateCategory(stored_category.pk, name)
        assert result is None
        assert store.categories.get(stored_category.pk).name == name

    def test_remove_category(self, store, hamster_interface, stored_category):
        """Make sure that removing a category works as intended."""
        assert store.categories.get(stored_category.pk)
        result = hamster_interface.RemoveCategory(stored_category.pk)
        assert result is None
        with pytest.raises(KeyError):
            store.categories.get(stored_category.pk)

    def test_get_category(self, store, hamster_interface, stored_category):
        """Make sure we can look up a categories PK by its name."""
        result = hamster_interface.GetCategoryId(stored_category.name)
        assert result == stored_category.pk

    def test_get_categories(self, store, hamster_interface, stored_category_batch_factory):
        """Make sure we get all stored categories."""
        categories = stored_category_batch_factory(5)
        result = hamster_interface.GetCategories()
        assert len(result) == 5
        for category in categories:
            assert (category.pk, category.name) in result


class TestActivityMethods(object):
    """Make sure ``Activity`` related methods work as intended."""

    def test_add_activity(self, store, hamster_interface, activity, stored_category):
        """Make sure that passed ``Activity`` gets stored properly, including its category."""
        new_pk = hamster_interface.AddActivity(activity.name, stored_category.pk)
        assert new_pk > 0
        result = store.activities.get(new_pk)
        assert result.name == activity.name
        assert result.category == stored_category

    def test_add_activity_without_category(self, store, hamster_interface, activity):
        """Make sure that ``Activity.category = None`` works as expected."""
        new_pk = hamster_interface.AddActivity(activity.name, -1)
        assert new_pk > 0
        result = store.activities.get(new_pk)
        assert result.name == activity.name
        assert result.category is None

    def test_update_activity_name(self, store, hamster_interface, stored_activity):
        """Make sure updating ``Activity.name`` works as expected."""
        new_name = 'foobar' + stored_activity.name
        category_pk = stored_activity.category.pk
        result = hamster_interface.UpdateActivity(stored_activity.pk, new_name, category_pk)
        assert result is None
        result = store.activities.get(stored_activity.pk)
        assert result.name == new_name
        assert result.category == stored_activity.category

    def test_update_activity_category(self, store, hamster_interface, stored_activity,
            stored_category):
        """Make sure that updateing ``Activity.category`` with a different category works."""
        assert stored_activity.category != stored_category
        result = hamster_interface.UpdateActivity(stored_activity.pk, stored_activity.name,
            stored_category.pk)
        assert result is None
        result = store.activities.get(stored_activity.pk)
        assert result.category == stored_category

    def test_update_activity_category_none(self, store, hamster_interface, stored_activity):
        """Make sure that we can deal with ``category=None`` properly."""
        assert stored_activity.category is not None
        result = hamster_interface.UpdateActivity(stored_activity.pk, stored_activity.name, -1)
        assert result is None
        result = store.activities.get(stored_activity.pk)
        assert result.category is None

    def test_remove_activity(self, store, hamster_interface, stored_activity):
        """Make sure that the passed activity is actually removed."""
        result = hamster_interface.RemoveActivity(stored_activity.pk)
        assert result is None
        with pytest.raises(KeyError):
            store.activities.get(stored_activity.pk)

    @pytest.mark.xfail(reason='Missing hamsterlib API support. See #134.')
    def test_get_activities(self, store, hamster_interface, stored_activity):
        result = hamster_interface.GetActivities(category=stored_activity.category)
        assert len(store.activities.get_all(category=stored_activity.category)) == 1
        assert len(result) == 1

    def test_get_activity_by_name(self, store, hamster_interface, stored_activity):
        """Make sure we can look up an ``Activity`` by its ``name/categor`` composite key."""
        result = hamster_interface.GetActivityByName(stored_activity.name,
            stored_activity.category.pk, True)
        assert result['id'] == stored_activity.pk
        assert result['name'] == stored_activity.name
        assert result['deleted'] == stored_activity.deleted
        assert result['category'] == stored_activity.category.name

    def test_get_activity_by_name_no_category(self, store, hamster_interface,
            stored_activity_factory):
        """Make sure we can look up an ``Activity`` by its composite key if ``category=None``."""
        activity = stored_activity_factory(category=None)
        result = hamster_interface.GetActivityByName(activity.name, -1, True)
        assert result['id'] == activity.pk
        assert result['name'] == activity.name
        assert result['deleted'] == activity.deleted
        assert result['category'] == 'unsorted category'
