# -*- coding: utf-8 -*-

"""Integration tests for hamster_dbus.objects."""

import pytest

import hamster_dbus.helpers as helpers


@pytest.mark.needs_dbus_service
class TestCategoryManager(object):

    def test_save_new(self, category_manager, category, category_name_parametrized):
        """Make sure an instance is created and returned."""

        category.name = category_name_parametrized
        dbus_category = helpers.hamster_to_dbus_category(category)
        result = category_manager.Save(dbus_category)
        result = helpers.dbus_to_hamster_category(result)
        assert result.pk
        assert category.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    def test_get_or_create_created(self, category_manager, category):
        """Make sure an instance is created and returned."""
        assert not category_manager.GetAll()
        dbus_category = helpers.hamster_to_dbus_category(category)
        result = category_manager.GetOrCreate(dbus_category)
        result = helpers.dbus_to_hamster_category(result)
        assert result.pk
        assert category.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    def test_get_or_create_get(self, category_manager, stored_category):
        """If name exists make sure it is fetched and no new one created."""
        assert len(category_manager.GetAll()) == 1
        dbus_category = helpers.hamster_to_dbus_category(stored_category)
        result = category_manager.GetOrCreate(dbus_category)
        result = helpers.dbus_to_hamster_category(result)
        assert len(category_manager.GetAll()) == 1
        assert stored_category.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    def test_remove(self, category_manager, stored_category):
        """Make sure a category is removed."""
        result = category_manager.Remove(stored_category.pk)
        assert result is None
        # [FIXME]
        # with pytest.raises(KeyError):
        #    store.categories.get(stored_category.pk)

    def test_get(self, category_manager, stored_category):
        """Make sure a matching category is returned."""
        result = category_manager.Get(stored_category.pk)
        result = helpers.dbus_to_hamster_category(result)
        assert result.pk == stored_category.pk
        assert result.name == stored_category.name

    def test_get_by_name(self, category_manager, stored_category):
        """Make sure a matching category is returned."""
        result = category_manager.GetByName(stored_category.name)
        result = helpers.dbus_to_hamster_category(result)
        assert result.pk == stored_category.pk
        assert result.name == stored_category.name

    def test_get_all(self, category_manager, stored_category_batch_factory):
        """Make sure we get all stored categories."""
        categories = stored_category_batch_factory(5)
        result = category_manager.GetAll()
        result = [helpers.dbus_to_hamster_category(each) for each in result]
        assert len(result) == 5
        for category in categories:
            assert category in result


@pytest.mark.needs_dbus_service
class TestActivityManager(object):

    def test_save_new(self, activity_manager, activity):
        """Make sure instance is saved and returned."""
        dbus_activity = helpers.hamster_to_dbus_activity(activity)
        result = activity_manager.Save(dbus_activity)
        result = helpers.dbus_to_hamster_activity(result)
        assert result.pk
        assert result.name == activity.name
        # We create a new instance, hence result will have a pk where the
        # original does not.
        assert activity.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    def test_remove(self, activity_manager, stored_activity):
        """Make sure instance is removed."""
        result = activity_manager.Remove(stored_activity.pk)
        assert result is None
        # [FIXME]
        # with pytest.raises(KeyError):
        #     store.activities.get(stored_activity.pk)

    def test_get(self, activity_manager, stored_activity):
        """Make sure instance is returned."""
        result = activity_manager.Get(stored_activity.pk)
        result = helpers.dbus_to_hamster_activity(result)
        assert result == stored_activity

    def test_get_all(self, activity_manager, stored_activity_batch_factory):
        """Make sure we get all stored categories."""
        activities = stored_activity_batch_factory(5)
        result = activity_manager.GetAll(-2)
        result = [helpers.dbus_to_hamster_activity(each) for each in result]
        assert len(result) == 5
        for activity in activities:
            assert activity in result


@pytest.mark.needs_dbus_service
class TestTagManager(object):

    def test_save_new(self, tag_manager, tag, tag_name_parametrized):
        """Make sure an instance is created and returned."""

        tag.name = tag_name_parametrized
        dbus_tag = helpers.hamster_to_dbus_tag(tag)
        result = tag_manager.Save(dbus_tag)
        result = helpers.dbus_to_hamster_tag(result)
        assert result.pk
        assert tag.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    def test_remove(self, tag_manager, stored_tag):
        """Make sure a tag is removed."""
        result = tag_manager.Remove(stored_tag.pk)
        assert result is None
        # [FIXME]
        # with pytest.raises(KeyError):
        #    store.categories.get(stored_tag.pk)

    def test_get_by_name(self, tag_manager, stored_tag):
        """Make sure a matching tag is returned."""
        result = tag_manager.GetByName(stored_tag.name)
        result = helpers.dbus_to_hamster_tag(result)
        assert result.pk == stored_tag.pk
        assert result.name == stored_tag.name

    def test_get_all(self, tag_manager, stored_tag_batch_factory):
        """Make sure we get all stored categories."""
        tags = stored_tag_batch_factory(5)
        result = tag_manager.GetAll()
        result = [helpers.dbus_to_hamster_tag(each) for each in result]
        assert len(result) == 5
        for tag in tags:
            assert tag in result


@pytest.mark.needs_dbus_service
class TestFactManager(object):

    def test_save_new(self, fact_manager, fact):
        """Make sure instance is saved and returned."""
        dbus_fact = helpers.hamster_to_dbus_fact(fact)
        result = fact_manager.Save(dbus_fact)
        result = helpers.dbus_to_hamster_fact(result)
        assert fact.as_tuple(include_pk=False) == result.as_tuple(include_pk=False)

    def test_remove(self, fact_manager, stored_fact):
        """Make sure instance is removed."""
        result = fact_manager.Remove(stored_fact.pk)
        assert result is None
        # [FIXME]
        # with pytest.raises(KeyError):
        #     store.facts.get(pk)

    def test_get(self, fact_manager, stored_fact):
        """Make sure instance is returned."""
        result = fact_manager.Get(stored_fact.pk)
        result = helpers.dbus_to_hamster_fact(result)
        assert result == stored_fact

    # [FIXME]
    # This should be expanded
    def test_get_all(self, fact_manager, stored_fact_batch_factory):
        """Make sure we get all matching instances."""
        stored_fact_batch_factory(5)
        result = fact_manager.GetAll('', '', '')
        assert len(result) == 5
