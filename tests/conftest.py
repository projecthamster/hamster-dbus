import pytest
import subprocess
import dbus



@pytest.fixture
def subprocess_service():
    """Provide a running service fixture using the ``subpprocess`` approach."""
    env = os.environ.copy()
    subprocess.Popen(['python', 'hamster_dbus/hamster_dbus.py', 'server'], env=env)
    time.sleep(1)
    print(subprocess)


@pytest.fixture
def subprocess_remote_service(subprocess_service):
    bus = dbus.SessionBus()
    remote_object = bus.get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus')
    return remote_object


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
