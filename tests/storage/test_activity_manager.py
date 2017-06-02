# -*- coding: utf-8 -*-

"""
Unittests for ``hamster_dbus.storage.ActivityManager``.

Please refer to ``__init__.py`` for general details.
"""

from __future__ import absolute_import, unicode_literals

import subprocess

import dbus
import dbusmock
from hamster_lib import objects as lib_objects

from hamster_dbus import storage

from . import common
from .. import factories


class BaseTestActivityManager(common.HamsterDBusManagerTestCase):
    """Base test case that provides infrastructure common to all other test cases."""

    def setUp(self):
        """
        Setup a mock ``ActivityManager`` object and provide a convenient interface.

        By adding methods to ``self.interface`` individual tests can mock an available
        dbus object while ``self.manager`` provides easy access to an actual
        ``ActivityManager`` instance. By explicitly passing our test session bus
        we make sure the manager queries against the right bus/object.
        """
        self.service_mock = self.spawn_server(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/ActivityManager',
            'org.projecthamster.HamsterDBus.ActivityManager1',
            stdout=subprocess.PIPE
        )

        self.dbus_object = self.dbus_con.get_object(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/ActivityManager'
        )

        self.interface = dbus.Interface(self.dbus_object, dbusmock.MOCK_IFACE)
        self.manager = storage.ActivityManager(bus=self.dbus_con)


class TestSave(BaseTestActivityManager):

    def setUp(self):
        """Test setup."""
        super(TestSave, self).setUp()
        self.existing_activity = factories.ActivityFactory(pk=1)

    def test_existing(self):
        """Make sure saving an existing activity returns an ``Activity`` instance."""
        self.dbus_object.AddMethod(
            '', 'Save', '(is(is)b)', '(is(is)b)', 'ret = (1, "foo", (1, "bar"), False)'
        )

        result = self.manager.save(self.existing_activity)
        self.assertIsInstance(result, lib_objects.Activity)

    def test_save_non_activivty(self):
        """Make sure that saving anything but an ``Activity`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.save('foobar')


class TestGetOrCreate(BaseTestActivityManager):

    def setUp(self):
        """Test setup."""
        super(TestGetOrCreate, self).setUp()
        self.new_activivty = factories.ActivityFactory(pk=None)
        self.existing_activity = factories.ActivityFactory(pk=1)

    def test_existing_activity(self):
        """Make sure passing an existing activity returns an ``Activity`` instance."""
        self.dbus_object.AddMethod(
            '', 'GetOrCreate', '(is(is)b)', '(is(is)b)', 'ret = (1, "foo", (1, "bar"), False)'
        )

        result = self.manager.get_or_create(self.existing_activity)
        self.assertIsInstance(result, lib_objects.Activity)

    def test_new_activity(self):
        """Make sure passing a new activity returns an ``Activity`` instance."""
        self.dbus_object.AddMethod(
            '', 'GetOrCreate', '(is(is)b)', '(is(is)b)', 'ret = (1, "foo", (1, "bar"), False)'
        )

        result = self.manager.get_or_create(self.new_activivty)
        self.assertIsInstance(result, lib_objects.Activity)

    def test_save_non_activivty(self):
        """Make sure that saving anything but an ``Activity`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.get_or_create('string')


class TestRemove(BaseTestActivityManager):

    def setUp(self):
        """Test setup."""
        super(TestRemove, self).setUp()
        self.existing_activity = factories.ActivityFactory(pk=1)

    def test_remove_existing(self):
        """Make sure that removing an ``Activity`` returns ``True``."""
        self.dbus_object.AddMethod('', 'Remove', 'i', '', '')

        result = self.manager.remove(self.existing_activity)
        self.assertTrue(result)

    def test_save_non_activivty(self):
        """Make sure that saving anything but an ``Activity`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.remove('string')


class TestGet(BaseTestActivityManager):

    def setUp(self):
        """Test setup."""
        super(TestGet, self).setUp()
        self.existing_activity = factories.ActivityFactory(pk=1)

    def test_get_existing(self):
        """Make sure an ``Activity`` instance is returned."""

        self.dbus_object.AddMethod(
            '', 'Get', 'i', '(is(is)b)', 'ret = (1, "foo", (1, "bar"), False)'
        )

        result = self.manager.get(self.existing_activity.pk)
        self.assertIsInstance(result, lib_objects.Activity)


class TestGetByComposite(BaseTestActivityManager):

    def setUp(self):
        """Test setup."""
        super(TestGetByComposite, self).setUp()
        self.existing_activity = factories.ActivityFactory(pk=1)

    def test_with_category(self):
        """Make sure an ``Activity`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'GetByComposite', 's(is)', '(is(is)b)', 'ret = (1, "foo", (1, "bar"), False)'
        )

        result = self.manager.get_by_composite(
            # [FIXME]
            # It looks like ``python-dbusmock`` is not truely python 2
            # compatible and uses problematic ``str``-casts.
            # self.existing_activity.name, self.existing_activity.category
            'fooo', self.existing_activity.category
        )
        self.assertIsInstance(result, lib_objects.Activity)

    def test_without_category(self):
        """Make sure an ``Activity`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'GetByComposite', 's(is)', '(is(is)b)', 'ret = (1, "foo", (-2, ""), False)'
        )

        # [FIXME]
        # It looks like ``python-dbusmock`` is not truely python 2
        # compatible and uses problematic ``str``-casts.
        # self.existing_activity.name, self.existing_activity.category
        result = self.manager.get_by_composite('fooo', None)
        self.assertIsInstance(result, lib_objects.Activity)

    def test_invalid_category_type(self):
        """Make sure that anything but an ``Activity`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.get_by_composite('foo', 'category1')


class TestGetAll(BaseTestActivityManager):

    def setUp(self):
        """Test setup."""
        super(TestGetAll, self).setUp()
        self.existing_category = factories.CategoryFactory(pk=1)

    def test_filter_by_existing_category(self):
        """Make sure an iterator of ``Activity`` instances is returned."""
        self.dbus_object.AddMethod(
            '', 'GetAll', 'is', 'a(is(is)b)', 'ret = [(1, "foo", (1, "bar"), False)]'
        )

        result = self.manager.get_all(self.existing_category, 'foobar')
        for each in result:
            self.assertIsInstance(each, lib_objects.Activity)

    def test_filter_without_category(self):
        """Make sure an iterator of ``Activity`` instances is returned."""
        self.dbus_object.AddMethod(
            '', 'GetAll', 'is', 'a(is(is)b)', 'ret = [(1, "foo", (1, "bar"), False)]'
        )

        result = self.manager.get_all(None, 'foobar')
        for each in result:
            self.assertIsInstance(each, lib_objects.Activity)

    def test_allow_all_categories(self):
        """Make sure an iterator of ``Activity`` instances is returned."""
        self.dbus_object.AddMethod(
            '', 'GetAll', 'is', 'a(is(is)b)', 'ret = [(1, "foo", (1, "bar"), False)]'
        )

        result = self.manager.get_all(category=False, search_term='foo')
        for each in result:
            self.assertIsInstance(each, lib_objects.Activity)

    def test_invalid_category(self):
        """Make sure that anything but an ``Category`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.get_all('category', 'foo')
