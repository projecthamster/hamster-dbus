"""General fixtures."""
from __future__ import absolute_import, unicode_literals

import datetime
import os
import signal
import subprocess
import time

import dbus
import dbusmock
import fauxfactory
import pytest
from pytest_factoryboy import register

from hamster_dbus import helpers

from .. import factories

register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.TagFactory)
register(factories.FactFactory)

# [FIXME]
# At several places we use ``faker.word`` instead of the original faked value.
# If I remember correctly this is due to probems with ``dbusmock`` under python2
# rather than our own code, but still this should at least be documented
# somewhere.


@pytest.fixture
def private_session_bus(request):
    """
    Launch a new 'private' session bus and return the connection instance.

    This is done so that we do not 'pollute' the testing users session bus.

    We can not use dbusmock classmethod as it does not return the PID, which
    we need in order to kill the process in the finalizer.
    """
    def fin():
        dbusmock.testcase.DBusTestCase.stop_dbus(pid)

    def start_bus():
        argv = ['dbus-launch']
        out = subprocess.check_output(argv, universal_newlines=True)
        variables = {}
        for line in out.splitlines():
            (k, v) = line.split('=', 1)
            variables[k] = v
        return (int(variables['DBUS_SESSION_BUS_PID']),
                variables['DBUS_SESSION_BUS_ADDRESS'])

    request.addfinalizer(fin)

    pid, address = start_bus()
    os.environ['DBUS_SESSION_BUS_ADDRESS'] = address
    time.sleep(0.5)

    dbus_con = dbus.bus.BusConnection(os.environ['DBUS_SESSION_BUS_ADDRESS'])
    return dbus_con


@pytest.fixture
def live_service(request, private_session_bus):
    """
    Provide a running hamster service hooked into a private session bus.

    Returns the 'daemon' ``Popen`` object as well as the bus connection it has
    been launched on.

    Note: The way a launched service determines the bus to connect to is by
    inspecting ``DBUS_SESSION_BUS_ADDRESS`` ENVVAR. If this would be empty,
    the default session bus is used.
    """
    def fin():
        os.kill(daemon.pid, signal.SIGTERM)

    request.addfinalizer(fin)

    daemon = subprocess.Popen(['hamster_dbus/hamster_dbus_service.py', 'server'])
    dbusmock.testcase.DBusTestCase.wait_for_bus_object(
        'org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus/ActivityManager',
    )
    bus = private_session_bus
    return daemon, bus


@pytest.fixture
def hamster_dbus_interface(request, live_service):
    """Provide a convenient object hook to our hamster-dbus service."""
    daemon, bus = live_service
    object_ = bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus1')
    return interface


@pytest.fixture
def category_manager(request, live_service):
    """Provide a convenient object hook to our hamster-dbus service."""
    daemon, bus = live_service
    object_ = bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus/CategoryManager')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus.CategoryManager1')
    return interface


@pytest.fixture
def activity_manager(request, live_service):
    """Provide a convenient object hook to our hamster-dbus service."""
    daemon, bus = live_service
    object_ = bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus/ActivityManager')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus.ActivityManager1')
    return interface


@pytest.fixture
def tag_manager(request, live_service):
    """Provide a convenient object hook to our hamster-dbus service."""
    daemon, bus = live_service
    object_ = bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus/TagManager')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus.TagManager1')
    return interface


@pytest.fixture
def fact_manager(request, live_service):
    """Provide a convenient object hook to our hamster-dbus service."""
    daemon, bus = live_service
    object_ = bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus/FactManager')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus.FactManager1')
    return interface


# Data
@pytest.fixture(params=[
    fauxfactory.gen_alpha(),
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
    fauxfactory.gen_cjk(),
])
def category_name_parametrized(request):
    """Provide a huge variety of possible ``Category.name`` strings."""
    return request.param


@pytest.fixture(params=[
    fauxfactory.gen_alpha(),
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
    fauxfactory.gen_cjk(),
])
def activity_name_parametrized(request):
    """Provide a huge variety of possible ``Activity.name`` strings."""
    return request.param


@pytest.fixture(params=[
    fauxfactory.gen_alpha(),
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
    fauxfactory.gen_cjk(),
])
def tag_name_parametrized(request):
    """Provide a huge variety of possible ``Tag.name`` strings."""
    return request.param


# Stored instances
@pytest.fixture
def stored_category_factory(request, category_manager, category_factory, faker):
    """
    A factory for category instances that are present in our persistent store.

    Because we do not have access to the actual store we need to assume that
    the ``Save`` method works as expected.
    """
    def factory(**kwargs):
        category = category_factory.build(**kwargs)
        result = category_manager.Save(helpers.hamster_to_dbus_category(category))
        return helpers.dbus_to_hamster_category(result)
    return factory


@pytest.fixture
def stored_category(request, stored_category_factory):
    """A singe persistent category instances."""
    return stored_category_factory()


@pytest.fixture
def stored_category_batch_factory(request, stored_category_factory, faker):
    """A factory for category instances that are present in our persistent store."""
    def factory(amount):
        categories = []
        for i in range(amount):
            categories.append(stored_category_factory(name=faker.word()))
        return categories
    return factory


@pytest.fixture
def stored_activity_factory(request, activity_manager, activity_factory, faker):
    """
    A factory for activity instances that are present in our persistent store.

    Because we do not have access to the actual store we need to assume that
    the ``Save`` method works as expected.
    """
    def factory(**kwargs):
        activity = activity_factory.build(**kwargs)
        result = activity_manager.Save(helpers.hamster_to_dbus_activity(activity))
        return helpers.dbus_to_hamster_activity(result)
    return factory


@pytest.fixture
def stored_activity(request, stored_activity_factory):
    """A singe persistent activity instances."""
    return stored_activity_factory()


@pytest.fixture
def stored_activity_batch_factory(request, stored_activity_factory, faker):
    """Factory for batch creating persistent activity instances."""
    def factory(amount):
        activities = []
        for i in range(amount):
            activities.append(stored_activity_factory(name=faker.word()))
        return activities
    return factory


@pytest.fixture
def stored_tag_factory(request, tag_manager, tag_factory, faker):
    """
    A factory for tag instances that are present in our persistent store.

    Because we do not have access to the actual store we need to assume that
    the ``Save`` method works as expected.
    """
    def factory(**kwargs):
        tag = tag_factory.build(**kwargs)
        result = tag_manager.Save(helpers.hamster_to_dbus_tag(tag))
        return helpers.dbus_to_hamster_tag(result)
    return factory


@pytest.fixture
def stored_tag(request, stored_tag_factory):
    """A singe persistent tag instances."""
    return stored_tag_factory()


@pytest.fixture
def stored_tag_batch_factory(request, stored_tag_factory, faker):
    """A factory for tag instances that are present in our persistent store."""
    def factory(amount):
        tags = []
        for i in range(amount):
            tags.append(stored_tag_factory(name=faker.word()))
        return tags
    return factory


@pytest.fixture
def stored_fact_factory(request, fact_manager, fact_factory, faker):
    """A factory for fact instances that are present in our persistent store."""
    def factory(**kwargs):
        fact = fact_factory.build(**kwargs)
        result = fact_manager.Save(helpers.hamster_to_dbus_fact(fact))
        return helpers.dbus_to_hamster_fact(result)
    return factory


@pytest.fixture
def stored_fact(request, stored_fact_factory):
    """A singe persistent fact instances."""
    return stored_fact_factory()


@pytest.fixture
def stored_fact_batch_factory(request, stored_fact_factory, faker):
    """
    Factory for batch creating persistent fact instances.

    Because we do not have access to the actual store we need to assume that
    the ``Save`` method works as expected.
    """
    def factory(amount):
        facts = []
        old_start = datetime.datetime.now()
        offset = datetime.timedelta(hours=4)
        for i in range(amount):
            start = old_start + offset
            fact = stored_fact_factory(start=start)
            facts.append(fact)
            old_start = start
        return facts
    return factory
