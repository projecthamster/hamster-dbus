# -*- coding: utf-8 -*-

"""
Unittests for ``hamster_dbus.storage.FactManager``.

Please refer to ``__init__.py`` for general details.
"""

from __future__ import absolute_import, unicode_literals

import datetime
import subprocess

import dbus
import dbusmock
from hamster_lib import objects as lib_objects

from hamster_dbus import storage

from . import common
from .. import factories


class BaseTestFactManager(common.HamsterDBusManagerTestCase):
    """Base test case that provides infrastructure common to all other test cases."""

    def setUp(self):
        """
        Setup a mock ``FactManager`` object and provide a convenient interface.

        By adding methods to ``self.interface`` individual tests can mock an available
        dbus object while ``self.manager`` provides easy access to an actual
        ``FactManager`` instance. By explicitly passing our test session bus
        we make sure the manager queries against the right bus/object.
        """
        self.service_mock = self.spawn_server(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/FactManager',
            'org.projecthamster.HamsterDBus.FactManager1',
            stdout=subprocess.PIPE
        )

        self.dbus_object = self.dbus_con.get_object(
            'org.projecthamster.HamsterDBus',
            '/org/projecthamster/HamsterDBus/FactManager'
        )

        self.interface = dbus.Interface(self.dbus_object, dbusmock.MOCK_IFACE)
        self.manager = storage.FactManager(bus=self.dbus_con)


class TestSave(BaseTestFactManager):

    def setUp(self):
        """Test setup."""
        super(TestSave, self).setUp()
        self.new_fact = factories.FactFactory()
        self.existing_fact = factories.FactFactory(pk=1)

    def test_save_existing(self):
        """Make sure a ``Fact`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'Save', '(isss(is(is)b)a(is))', '(isss(is(is)b)a(is))',
            'ret = (1, "2016-12-01 18:00:00", "2016-12-01 19:00:00", "description",'
            '(1, "foo", (2, "bar"), False), [(1, "tag1"), (2, "tag2")])'
        )

        result = self.manager.save(self.existing_fact)
        self.assertIsInstance(result, lib_objects.Fact)

    def test_save_new(self):
        """Make sure a ``Fact`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'Save', '(isss(is(is)b)a(is))', '(isss(is(is)b)a(is))',
            'ret = (1, "2016-12-01 18:00:00", "2016-12-01 19:00:00", "description",'
            '(1, "foo", (2, "bar"), False), [(1, "tag1"), (2, "tag2")])'
        )

        result = self.manager.save(self.new_fact)
        self.assertIsInstance(result, lib_objects.Fact)

    def test_non_fact_instance(self):
        """Make sure that passing anything but a ``Fact`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.save('foobar')


class TestRemove(BaseTestFactManager):

    def setUp(self):
        """Test setup."""
        super(TestRemove, self).setUp()
        self.existing_fact = factories.FactFactory(pk=1)

    def test_remove(self):
        """Make sure ``None`` is returned."""
        self.dbus_object.AddMethod('', 'Remove', 'i', '', '')

        result = self.manager.remove(self.existing_fact)
        self.assertIsNone(result)

    def test_remove_non_fact(self):
        """Make sure that passing anything but a ``Fact`` instance throws an error."""
        with self.assertRaises(TypeError):
            self.manager.remove(1)


class TestGet(BaseTestFactManager):

    def setUp(self):
        """Test setup."""
        super(TestGet, self).setUp()
        self.existing_fact = factories.FactFactory(pk=1)

    def test_get(self):
        """Make sure a ``Fact`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'Get', 'i', '(isss(is(is)b)a(is))',
            'ret = (1, "2016-12-01 18:00:00", "2016-12-01 19:00:00", "description",'
            '(1, "foo", (2, "bar"), False), [(1, "tag1"), (2, "tag2")])'
        )

        result = self.manager.get(self.existing_fact.pk)
        self.assertIsInstance(result, lib_objects.Fact)


class TestGetAll(BaseTestFactManager):

    def test_get_all(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod(
            '', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))',
            'ret = [(1, "2016-12-01 18:00:00", "2016-12-01 19:00:00", "description",'
            '(1, "foo", (2, "bar"), False), [(1, "tag1"), (2, "tag2")])]'
        )

        result = self.manager.get_all()
        for each in result:
            self.assertIsInstance(each, lib_objects.Fact)

    def test_start_datetime(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(start=datetime.datetime(2017, 2, 1, 17))
        self.assertIsInstance(result, list)

    def test_start_date(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(start=datetime.date(2017, 2, 1))
        self.assertIsInstance(result, list)

    def test_start_time(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(start=datetime.time(17))
        self.assertIsInstance(result, list)

    def test_start_none(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(start=None)
        self.assertIsInstance(result, list)

    def test_invalid_start_type(self):
        """Make sure that passing an invalid ``start`` argument throws an error."""
        with self.assertRaises(TypeError):
            self.manager.get_all(start='2012-02-01 13:30')

    def test_end_datetime(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(end=datetime.datetime(2017, 2, 1, 17))
        self.assertIsInstance(result, list)

    def test_end_date(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(end=datetime.date(2017, 2, 1))
        self.assertIsInstance(result, list)

    def test_end_time(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(end=datetime.time(17))
        self.assertIsInstance(result, list)

    def test_end_none(self):
        """Make sure a iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod('', 'GetAll', 'sss', 'a(isss(is(is)b)a(is))', 'ret = []')

        result = self.manager.get_all(end=None)
        self.assertIsInstance(result, list)

    def test_invalid_end_type(self):
        """Make sure that passing an invalid ``end`` argument throws an error."""
        with self.assertRaises(TypeError):
            self.manager.get_all(end='2012-02-01 13:30')

    def test_end_before_start(self):
        """Make sure that passing an ``end<start`` throws an error."""
        with self.assertRaises(ValueError):
            self.manager.get_all(
                start=datetime.datetime(2017, 2, 2, 18),
                end=datetime.datetime(2017, 2, 1, 18)
            )


class TestGetToday(BaseTestFactManager):

    def test_get(self):
        """Make sure a  iterator of ``Fact`` instances is returned."""
        self.dbus_object.AddMethod(
            '', 'GetToday', '', 'a(isss(is(is)b)a(is))',
            'ret = [(1, "2016-12-01 18:00:00", "2016-12-01 19:00:00", "description",'
            '(1, "foo", (2, "bar"), False), [(1, "tag1"), (2, "tag2")])]'
        )

        result = self.manager.get_today()
        for each in result:
            self.assertIsInstance(each, lib_objects.Fact)


class TestStopTmpFact(BaseTestFactManager):

    def setUp(self):
        super(TestStopTmpFact, self).setUp()

    def test_stop_tmp_fact(self):
        """Make sure a ``Fact`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'StopTmpFact', '', '(isss(is(is)b)a(is))',
            'ret = (1, "2016-12-01 18:00:00", "2016-12-01 19:00:00", "description",'
            '(1, "foo", (2, "bar"), False), [(1, "tag1"), (2, "tag2")])'
        )

        result = self.manager.stop_tmp_fact()
        self.assertIsInstance(result, lib_objects.Fact)


class TestCancelTmpFact(BaseTestFactManager):

    def test_cancel_tmp_fact(self):
        """Make sure ``None`` is returned."""
        self.dbus_object.AddMethod(
            '', 'CancelTmpFact', '', '', '')

        result = self.manager.cancel_tmp_fact()
        self.assertIsNone(result)


class TestGetTmpFact(BaseTestFactManager):

    def test_stop_tmp_fact(self):
        """Make sure a ``Fact`` instance is returned."""
        self.dbus_object.AddMethod(
            '', 'GetTmpFact', '', '(isss(is(is)b)a(is))',
            'ret = (1, "2016-12-01 18:00:00", "2016-12-01 19:00:00", "description",'
            '(1, "foo", (2, "bar"), False), [(1, "tag1"), (2, "tag2")])'
        )

        result = self.manager.get_tmp_fact()
        self.assertIsInstance(result, lib_objects.Fact)
