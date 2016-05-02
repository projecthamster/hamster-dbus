import pytest
import signal
import subprocess
import dbus
import os
import errno
import time

# Adaption of testup ised in TtestHamsterDBusServiceDbusMockStyle

@pytest.fixture
def init_session_bus(request):
    """
    Provide a new private session bus so we don't polute the regular one.

    This is a straight copy of: https://github.com/martinpitt/python-dbusmock/blob/master/dbusmock/testcase.py#L92

    Returns:
        tuple: (pid, address) pair.
    """
    def fin():
        try:
            del os.environ['DBUS_SESSION_BUS_ADDRESS']
        except KeyError:
            pass
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        timeout = 5
        while timeout > 0:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    break
                else:
                    raise
            time.sleep(0.1)
        else:
            sys.stderr.write('ERROR: timed out waiting for bus process to terminate\n')
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

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
        os.kill(deamon.pid, signal.SIGKILL)
    env = os.environ.copy()
    deamon = subprocess.Popen([sys.executable, '-m', 'hamster_dbus.hamster_dbus', 'server'], env=env)
    # Wait for the service to become available
    time.sleep(2)
    request.addfinalizer(fin)
    return deamon


@pytest.fixture
def hamster_interface(request, session_bus, hamster_service):
    """Provide a covinient interface hook to our hamster-dbus service."""
    return session_bus.get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus')





# END



#@pytest.fixture
#def subprocess_service():
#    """Provide a running service fixture using the ``subpprocess`` approach."""
#    env = os.environ.copy()
#    subprocess.Popen(['python', 'hamster_dbus/hamster_dbus.py', 'server'], env=env)
#    time.sleep(1)
#    print(subprocess)
#
#
#@pytest.fixture
#def subprocess_remote_service(subprocess_service):
#    bus = dbus.SessionBus()
#    remote_object = bus.get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus')
#    return remote_object
#
#
#@pytest.yield_fixture()
#def mock_loop():
#    DBusGMainLoop(set_as_default=True)
#    loop = GLib.MainLoop()
#    yield loop.run()
#    loop.quit()
#
#
#@pytest.fixture
#def mock_service2():
#    nv = os.environ.copy()
#    subprocess.Popen(['python', '../hamster_dbus/hamster_dbus.py', 'server'], env=env)
#    # Wait for the service to become available
#    time.sleep(1)
#
#@pytest.yield_fixture()
#def mock_service(mock_loop):
#    def launch_service(mock_loop):
#        loop.run()
#        myservice = hamster_dbus.HamsterDBusService()
#    thread = Thread(target=launch_service)
#    thread.start()
#    print(thread)
#    yield
#    mock_loop.quit()
#
#
#@pytest.fixture
#def remote_object(mock_loop, mock_service):
#    bus = dbus.SessionBus(mainloop=mock_loop)
#    remote_object = bus.get_object('org.gnome.hamster_dbus', '/fo')
#    return remote_object
#
#@pytest.yield_fixture
#def service4():
#    DBusGMainLoop(set_as_default=True)
#    loop = GLib.MainLoop()
#    loop.run()
#    myservice = hamster_dbus.HamsterDBusService()
#    yield loop
#    loop.quit()
