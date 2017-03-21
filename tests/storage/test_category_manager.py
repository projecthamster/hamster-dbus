# -*- coding: utf-8 -*-

"""
Unittests for ``hamster_dbus.storage.CategoryManager``.

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


class BaseTestCategoryManager(common.HamsterDBusManagerTestCase):
    """Base test case that provides infrastructure common to all other test cases."""

    def setUp(self):
        """
        Setup a mock ``CategoryManager`` object and provide a convenient interface.

        By adding methods to ``self.interface`` individual tests can mock an available
        dbus object while ``self.manager`` provides easy access to an actual
        ``CategoryManager`` instance. By explicitly passing our test session bus
        we make sure the manager queries against the right bus/object.
        """
        self.service_mock = self.spawn_server(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/CategoryManager',
            'org.projecthamster.HamsterDBus.CategoryManager1',
            stdout=subprocess.PIPE
        )

        self.dbus_object = self.dbus_con.get_object(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/CategoryManager'
        )

        self.interface = dbus.Interface(self.dbus_object, dbusmock.MOCK_IFACE)
        self.manager = storage.CategoryManager(bus=self.dbus_con)


class TestSave(BaseTestCategoryManager):

    def setUp(self):
        """Test setup."""
        super(TestSave, self).setUp()
        self.existing_category = factories.CategoryFactory(pk=1)

    def test_save(self):
        """Make sure a ``Category`` instance is returned."""
        self.dbus_object.AddMethod('', 'Save', '(is)', '(is)', 'ret = (1, "foo")')

        result = self.manager.save(self.existing_category)
        self.assertIsInstance(result, lib_objects.Category)

    def test_save_non_category(self):
        """Make sure that passing anything but a ``Category`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.save('foobar')


class TestGetOrCreate(BaseTestCategoryManager):

    def setUp(self):
        """Test setup."""
        super(TestGetOrCreate, self).setUp()
        self.new_category = factories.CategoryFactory()
        self.existing_category = factories.CategoryFactory(pk=1)

    def test_get_or_create_get(self):
        """Make sure a ``Category`` instance is returned."""
        self.dbus_object.AddMethod('', 'GetOrCreate', '(is)', '(is)', 'ret = (1, "foo")')

        result = self.manager.get_or_create(self.existing_category)
        self.assertIsInstance(result, lib_objects.Category)

    def test_get_or_create_create(self):
        """Make sure a ``Category`` instance is returned."""
        self.dbus_object.AddMethod('', 'GetOrCreate', '(is)', '(is)', 'ret = (1, "foo")')

        result = self.manager.get_or_create(self.new_category)
        self.assertIsInstance(result, lib_objects.Category)

    def test_non_category_instance(self):
        """Make sure that passing anything but a ``Category`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.get_or_create('foobar')


class TestRemove(BaseTestCategoryManager):

    def setUp(self):
        """Test setup."""
        super(TestRemove, self).setUp()
        self.existing_category = factories.CategoryFactory(pk=1)

    def test_remove(self):
        """Make sure a ``None`` is returned."""
        self.dbus_object.AddMethod('', 'Remove', 'i', '', '')
        result = self.manager.remove(self.existing_category)
        self.assertIsNone(result)

    def test_non_category_instance(self):
        """Make sure that passing anything but a ``Category`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.remove(1)


class TestGet(BaseTestCategoryManager):

    def setUp(self):
        """Test setup."""
        super(TestGet, self).setUp()
        self.existing_category = factories.CategoryFactory(pk=1)

    def test_get(self):
        """Make sure a ``Category`` instance is returned."""
        self.dbus_object.AddMethod('', 'Get', 'i', '(is)', 'ret = (1, "foo")')
        result = self.manager.get(self.existing_category.pk)
        self.assertIsInstance(result, lib_objects.Category)


class TestGetByName(BaseTestCategoryManager):
    def test_get_by_name(self):
        """Make sure a ``Category`` instance is returned."""
        self.dbus_object.AddMethod('', 'GetByName', 's', '(is)', 'ret = (1, "foo")')
        # [FIXME]
        # Due to problems with dbusmock under python 2
        result = self.manager.get_by_name('foobar')
        self.assertIsInstance(result, lib_objects.Category)


class TestGetAll(BaseTestCategoryManager):
    def test_get_all(self):
        """Make sure an iterator of ``Category`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', '', 'a(is)', 'ret = [(1, "foo"), (2, "bar")]')
        result = self.manager.get_all()
        for each in result:
            self.assertIsInstance(each, lib_objects.Category)
