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
