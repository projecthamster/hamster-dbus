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


class BaseTestTagManager(common.HamsterDBusManagerTestCase):
    """Base test case that provides infrastructure common to all other test cases."""

    def setUp(self):
        """
        Setup a mock ``TagyManager`` object and provide a convenient interface.

        By adding methods to ``self.interface`` individual tests can mock an available
        dbus object while ``self.manager`` provides easy access to an actual
        ``TagManager`` instance. By explicitly passing our test session bus
        we make sure the manager queries against the right bus/object.
        """
        self.service_mock = self.spawn_server(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/TagManager',
            'org.projecthamster.HamsterDBus.TagManager1',
            stdout=subprocess.PIPE
        )

        self.dbus_object = self.dbus_con.get_object(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/TagManager'
        )

        self.interface = dbus.Interface(self.dbus_object, dbusmock.MOCK_IFACE)
        self.manager = storage.TagManager(bus=self.dbus_con)


class TestSave(BaseTestTagManager):

    def setUp(self):
        """Test setup."""
        super(TestSave, self).setUp()
        self.existing_tag = factories.TagFactory(pk=1)

    def test_save(self):
        """Make sure a ``Tag`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'Save', '(is)', '(is)', 'ret = (1, "foo")'
        )

        result = self.manager.save(self.existing_tag)
        self.assertIsInstance(result, lib_objects.Tag)

    def test_save_non_activivty(self):
        """Make sure that passing anything but a ``Tag`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.save('foobar')


class TestGetOrCreate(BaseTestTagManager):

    def setUp(self):
        """Test setup."""
        super(TestGetOrCreate, self).setUp()
        self.new_tag = factories.TagFactory(pk=None)
        self.existing_tag = factories.TagFactory(pk=1)

    def test_get(self):
        """Make sure a ``Tag`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'GetOrCreate', '(is)', '(is)', 'ret = (1, "foo")'
        )
        result = self.manager.get_or_create(self.existing_tag)
        self.assertIsInstance(result, lib_objects.Tag)

    def test_create(self):
        """Make sure a ``Tag`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'GetOrCreate', '(is)', '(is)', 'ret = (1, "foo")'
        )
        result = self.manager.get_or_create(self.new_tag)
        self.assertIsInstance(result, lib_objects.Tag)

    def test_not_tag_instance(self):
        """Make sure that passing anything but a ``Tag`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.get_or_create('foobar')


class TestRemove(BaseTestTagManager):

    def setUp(self):
        """Test setup."""
        super(TestRemove, self).setUp()
        self.existing_tag = factories.TagFactory(pk=1)

    def test_remove(self):
        """Make sure ``None`` is returned."""
        self.dbus_object.AddMethod('', 'Remove', 'i', '', '')

        result = self.manager.remove(self.existing_tag)
        self.assertIsNone(result)

    def test_not_tag_instance(self):
        """Make sure that passing anything but a ``Tag`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.remove(1)


class TestGet(BaseTestTagManager):

    def setUp(self):
        """Test setup."""
        super(TestGet, self).setUp()
        self.existing_tag = factories.TagFactory(pk=1)

    def test_get(self):
        """Make sure a ``Tag`` instance is returned."""
        self.dbus_object.AddMethod('', 'Get', 'i', '(is)', 'ret = (1, "foo")')

        result = self.manager.get(self.existing_tag.pk)
        self.assertIsInstance(result, lib_objects.Tag)


class TestGetByName(BaseTestTagManager):

    def test_get_by_name(self):
        """Make sure a ``Tag`` instance is returned."""
        self.dbus_object.AddMethod('', 'GetByName', 's', '(is)', 'ret = (1, "foo")')

        result = self.manager.get_by_name('foo')
        self.assertIsInstance(result, lib_objects.Tag)


class TestGetAll(BaseTestTagManager):

    def test_get_all(self):
        """Make sure a iterator of ``Tag`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', '', 'a(is)', 'ret = [(1, "foo"), (2, "bar")]')

        result = self.manager.get_all()
        for each in result:
            self.assertIsInstance(each, lib_objects.Tag)
