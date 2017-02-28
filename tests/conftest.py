"""General fixtures."""

import datetime
import multiprocessing
import os
import signal
import subprocess
import time

import dbus
import fauxfactory
import hamster_lib
import pytest
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from pytest_factoryboy import register

from hamster_dbus.hamster_dbus import objects

from . import factories

register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.FactFactory)


@pytest.fixture()
def config(request, tmpdir):
    """A mocked up config."""
    return {
        'store': 'sqlalchemy',
        'day_start': datetime.time(5, 30, 0),
        'fact_min_delta': 60,
        'tmpfile_path': os.path.join(tmpdir.mkdir('hamster-dbus').strpath, 'tmpfile.pickle'),
        'db_engine': 'sqlite',
        'db_path': ':memory:'
    }


@pytest.fixture
def controller(request, config):
    """A hamster-lib controller instance that."""
    return hamster_lib.HamsterControl(config)


@pytest.fixture
def store(request, controller):
    """Just for the convenience of accessing our controllers store faster."""
    return controller.store


@pytest.fixture
def init_session_bus(request):
    """
    Provide a new private session bus so we don't polute the regular one.

    This is a straight copy of:
        https://github.com/martinpitt/python-dbusmock/blob/master/dbusmock/testcase.py#L92

    Returns:
        tuple: (pid, address) pair.
    """
    def fin():
        # [FIXME]
        # We propably could be a bit more gentle then this.
        os.kill(pid, signal.SIGKILL)

    argv = ['dbus-launch']
    out = subprocess.check_output(argv, universal_newlines=True)
    variables = {}
    for line in out.splitlines():
        (k, v) = line.split('=', 1)
        variables[k] = v
    pid = int(variables['DBUS_SESSION_BUS_PID'])
    request.addfinalizer(fin)
    return (pid, variables['DBUS_SESSION_BUS_ADDRESS'])


@pytest.fixture
def session_bus(init_session_bus, scope='session'):
    """
    Provide the session bus instance.

    Adapted from:
        https://github.com/martinpitt/python-dbusmock/blob/master/dbusmock/testcase.py#L137
    """
    if os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        return dbus.bus.BusConnection(os.environ['DBUS_SESSION_BUS_ADDRESS'])
    else:
        return dbus.SessionBus()


@pytest.fixture
def hamster_service(request, controller, session_bus, scope='session'):
    """
    Provide a dedicated serice that exposes our objects to be tested.

    We delegate loop setup and service instantiation to a new subprocess.
    Unline many examples we do not use ``process.join()`` as this would block our
    process indefinitly.
    Using pytest teardown mechanics will make sure we shut down the spawned process
    afterwards. This is where ``multiprocessing`` surpasses our ``threading`` based
    solution.
    """
    def run_service(controller):
        """Set up the mainloop and instanciate our dbus service class."""
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        objects.HamsterDBus(loop)
        objects.CategoryManager(controller)
        objects.ActivityManager(controller)
        objects.FactManager(controller)
        loop.run()

    def fin():
        """Shutdown the mainloop process."""
        process.terminate()

    process = multiprocessing.Process(target=run_service, args=(controller,))
    process.start()
    process.join(1)
    # Make sure we give it time to launch. Otherwise clients may query to early.
    time.sleep(0.5)
    request.addfinalizer(fin)
    return process


@pytest.fixture
def hamster_dbus(request, session_bus, hamster_service, scope='session'):
    """Provide a covenient object hook to our hamster-dbus service."""
    object_ = session_bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus')
    return interface


@pytest.fixture
def category_manager(request, session_bus, hamster_service):
    """Provide a covenient object hook to our hamster-dbus service."""
    object_ = session_bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus/CategoryManager')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus.CategoryManager1')
    return interface


@pytest.fixture
def activity_manager(request, session_bus, hamster_service):
    """Provide a covenient object hook to our hamster-dbus service."""
    object_ = session_bus.get_object('org.projecthamster.HamsterDBus',
        '/org/projecthamster/HamsterDBus/ActivityManager')
    interface = dbus.Interface(object_,
        dbus_interface='org.projecthamster.HamsterDBus.ActivityManager1')
    return interface


@pytest.fixture
def fact_manager(request, session_bus, hamster_service):
    """Provide a covenient object hook to our hamster-dbus service."""
    object_ = session_bus.get_object('org.projecthamster.HamsterDBus',
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


# Stored instances
@pytest.fixture
def stored_category_factory(request, store, category_factory, faker):
    """A factory for category instances that are present in our persistant store."""
    def factory(**kwargs):
        category = category_factory.build(**kwargs)
        return store.categories.save(category)
    return factory


@pytest.fixture
def stored_category(request, stored_category_factory):
    """A singe persistant category instances."""
    return stored_category_factory()


@pytest.fixture
def stored_category_batch_factory(request, stored_category_factory, faker):
    """A factory for category instances that are present in our persistant store."""
    def factory(amount):
        categories = []
        for i in range(amount):
            categories.append(stored_category_factory(name=faker.word()))
        return categories
    return factory


@pytest.fixture
def stored_activity_factory(request, store, activity_factory, faker):
    """A factory for activity instances that are present in our persistant store."""
    def factory(**kwargs):
        activity = activity_factory.build(**kwargs)
        return store.activities.save(activity)
    return factory


@pytest.fixture
def stored_activity(request, stored_activity_factory):
    """A singe persistant activity instances."""
    return stored_activity_factory()


@pytest.fixture
def stored_activity_batch_factory(request, stored_activity_factory, faker):
    """Factory for batch creating persistant activity instances."""
    def factory(amount):
        activities = []
        for i in range(amount):
            activities.append(stored_activity_factory(name=faker.word()))
        return activities
    return factory


@pytest.fixture
def stored_fact_factory(request, store, fact_factory, faker):
    """A factory for fact instances that are present in our persistant store."""
    def factory(**kwargs):
        fact = fact_factory.build(**kwargs)
        return store.facts.save(fact)
    return factory


@pytest.fixture
def stored_fact(request, stored_fact_factory):
    """A singe persistant fact instances."""
    return stored_fact_factory()


@pytest.fixture
def stored_fact_batch_factory(request, stored_fact_factory, faker):
    """Factory for batch creating persistant fact instances."""
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

@pytest.fixture
def current_fact(request, store, fact):
    """"Provide a 'current fact'."""
    fact.end = None
    return store.facts._start_tmp_fact(fact)
