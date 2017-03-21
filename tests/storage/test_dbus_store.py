# -*- coding: utf-8 -*-

"""
Unittests for DBusStore.

Please refer to ``__init__.py`` for general details.
"""

from __future__ import absolute_import, unicode_literals

import subprocess

from hamster_dbus import storage

from . import common


class TestDBusStore(common.HamsterDBusManagerTestCase):

    def setUp(self):
        """Setup test environment."""
        # We have to launch a mocked service in order to provide the
        # 'org.projecthamster.HamsterDBus' namespace.
        # Which object and interface does not actually matter for this test.
        self.service_mock = self.spawn_server(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/FactManager',
            'org.projecthamster.HamsterDBus.FactManager1',
            stdout=subprocess.PIPE
        )

        # For our test purpose, an empty config test suffices.
        self.store = storage.DBusStore({})

    def test_categories_manager(self):
        """Make sure a ``storage.CategoryManager`` is instantiated."""
        self.assertIsInstance(self.store.categories, storage.CategoryManager)

    def test_activities_manager(self):
        """Make sure a ``storage.ActivityManager`` is instantiated."""
        self.assertIsInstance(self.store.activities, storage.ActivityManager)

    def test_tags_manager(self):
        """Make sure a ``storage.TagManager`` is instantiated."""
        self.assertIsInstance(self.store.tags, storage.TagManager)

    def test_facts_manager(self):
        """Make sure a ``storage.FactManager`` is instantiated."""
        self.assertIsInstance(self.store.facts, storage.FactManager)

    def test_cleanup(self):
        """Test the cleanup method."""
        self.assertIsNone(self.store.cleanup())

    def test_explicit_bus(self):
        """Make sure that an explicitly passed bus is really used."""
        self.store = storage.DBusStore({}, bus=self.dbus_con)
        self.assertEqual(self.store._bus, self.dbus_con)
