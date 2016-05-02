import pytest
import signal
import subprocess
import dbus
import os
import errno
import time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib, GObject, Gtk

from hamster_dbus.hamster_dbus import HamsterDBusService


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
def hamster_service(request, session_bus):
    """
    Provide a hamster service running as a seperate process.

    This is heavily inspired by the way ``dbusmock`` sets up its ``mock_server``
    """
    import subprocess
    import sys
    import time
    import psutil
    def fin():
        # [FIXME]
        # We propably could be a bit more gentle then this.
        os.kill(deamon.pid, signal.SIGKILL)
    env = os.environ.copy()
    deamon = subprocess.Popen([sys.executable, '-m', 'hamster_dbus.hamster_dbus', 'server'], env=env)
    # Wait for the service to become available
    time.sleep(2)
    request.addfinalizer(fin)
    return deamon


@pytest.fixture
def hamster_service2(request, session_bus):
    """This roughly works but lacks a nice way to tear down."""
    import threading
    def run_service():
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        # Run needs to be called after we setup our service
        loop.run()
    def fin():
        thread.exit()
        raise TypeError
    thread = threading.Thread(target=run_service)
    thread.deamon = True
    thread.start()
    myservice = HamsterDBusService()
    #request.addfinalizer(fin)
    return thread


@pytest.fixture
def hamster_service3(request, session_bus):
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
    def run_service():
        """Set up the mainloop and instanciate our dbus service class."""
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        myservice = HamsterDBusService()
        loop.run()
    def fin():
        """Shutdown the mainloop process."""
        process.terminate()
    process = multiprocessing.Process(target=run_service)
    process.start()
    # Make sure we give it time to launch. Otherwise clients may query to early.
    time.sleep(2)
    request.addfinalizer(fin)
    return process



@pytest.fixture
def hamster_interface(request, session_bus, hamster_service3):
    """Provide a covinient interface hook to our hamster-dbus service."""
    time.sleep(2)
    return session_bus.get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus')
