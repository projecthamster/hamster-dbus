# -*- coding: utf-8 -*-

"""Module to provide a common base ``TestCase``."""


from __future__ import absolute_import, unicode_literals

import dbusmock


class HamsterDBusManagerTestCase(dbusmock.DBusTestCase):
    """
    Common testcase for storage backend unittests.

    This test case makes sure tests are run against a new private session bus
    instance and provides easy access to the underlying dbus connection.
    """

    @classmethod
    def setUpClass(cls):
        """Setup new private session bus."""
        cls.start_session_bus()
        cls.dbus_con = cls.get_dbus()

    def tearDown(self):
        """Terminate any service launched by the test case."""
        self.service_mock.terminate()
        self.service_mock.wait()
