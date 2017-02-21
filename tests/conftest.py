import pytest
import signal
import subprocess
import dbus
import os
import errno
import time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib, GObject, Gtk
from pytest_factoryboy import register
import datetime
import fauxfactory

from hamster_dbus.hamster_dbus import HamsterDBusService
import hamsterlib
from . import factories

register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.FactFactory)


@pytest.fixture()
def config(request, tmpdir):
    return {
        'store': 'sqlalchemy',
        'day_start': datetime.time(5, 30, 0),
        'fact_min_delta': 60,
        'tmpfile_path': '/tmp/tmpfile.pickle',
        'db_engine': 'sqlite',
        'db_path': os.path.join(tmpdir.mkdir('hamster-dbus').strpath, 'test.sqlite')
    }


@pytest.fixture
def controler(request, config):
    return hamsterlib.HamsterControl(config)


@pytest.fixture
def store(request, controler):
    """Just for the convenience of accessing our controlers store faster."""
    return controler.store


@pytest.fixture
def init_session_bus(request):
    """
    Provide a new private session bus so we don't polute the regular one.

    This is a straight copy of: https://github.com/martinpitt/python-dbusmock/blob/master/dbusmock/testcase.py#L92

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
def session_bus(init_session_bus):
    """
    Provide the session bus instance.

    Adapted from: https://github.com/martinpitt/python-dbusmock/blob/master/dbusmock/testcase.py#L137
    """
    if os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        return dbus.bus.BusConnection(os.environ['DBUS_SESSION_BUS_ADDRESS'])
    else:
        return dbus.SessionBus()


@pytest.fixture
def hamster_service(request, controler, session_bus):
    """
    This works as intended.

    We delegate loop setup and service instanciation to a new subprocess.
    Unline many examples we do not use ``process.join()`` as this would block our
    process indefinitly.
    Using pytest teardown mechanics will make sure we shut down the spawned process
    afterwards. This is where ``multiprocessing`` surpasses our ``threading`` based
    solution.
    """
    import multiprocessing
    def run_service(controler):
        """Set up the mainloop and instanciate our dbus service class."""
        GObject.threads_init()
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        service = HamsterDBusService(controler=controler)
        loop.run()

    def fin():
        """Shutdown the mainloop process."""
        process.terminate()

    process = multiprocessing.Process(target=run_service, args=(controler,))
    process.start()
    process.join(1)
    # Make sure we give it time to launch. Otherwise clients may query to early.
    time.sleep(1)
    request.addfinalizer(fin)
    return process


@pytest.fixture
def hamster_interface(request, session_bus, hamster_service):
    """Provide a covenient interface hook to our hamster-dbus service."""
    return session_bus.get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus')


# Data
@pytest.fixture(params=[
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
    fauxfactory.gen_cjk(),
])
def category_name_parametrized(request):
    return request.param


# Stored instances and factories
@pytest.fixture
def stored_category_factory(request, store, category_factory, faker):
    def factory(**kwargs):
        category = category_factory.build(name=faker.word())
        return store.categories.save(category)
    return factory


@pytest.fixture
def stored_category(request, stored_category_factory):
    return stored_category_factory()


@pytest.fixture
def stored_category_batch_factory(request, stored_category_factory, faker):
    def factory(amount):
        categories = []
        for i in range(amount):
            categories.append(stored_category_factory(name=faker.word()))
        return categories
    return factory


@pytest.fixture
def stored_activity_factory(request, store, activity_factory):
    def factory(**kwargs):
        activity = activity_factory.build(**kwargs)
        return store.activities.save(activity)
    return factory


@pytest.fixture
def stored_activity(request, stored_activity_factory):
    return stored_activity_factory()


@pytest.fixture
def stored_activity_batch_factory(request, stored_activity_factory, faker):
    def factory(amount):
        activities = []
        for i in range(amount):
            activities.append(stored_activity_factory(name=faker.word()))
        return activities
    return factory
