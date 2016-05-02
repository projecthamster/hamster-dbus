# -*- coding: utf-8 -*-

import pytest
import dbusmock
import os
import dbus
import psutil
import time
#from threading import Thread
#from dbus import GTestDBus


import hamster_dbus.hamster_dbus as hamster_dbus


#class TestHamsterDBusServiceMinimalCase(dbusmock.DBusTestCase):
#    @classmethod
#    def setuUpClass(klass):
#        klass.start_session_bus()
#        klass.dbus_con = klass.get_dbus()
#
#    def setUp(self):
#        import subprocess
#        import time
#        #self.service = hamster_dbus.HamsterDBusService()
#        env = os.environ.copy()
#    	self.p = subprocess.Popen(['python', 'hamster_dbus/hamster_dbus.py', 'server'], env=env)
#        # Wait for the service to become available
#        time.sleep(1)
#        assert self.p.stdout == None
#        assert self.p.stderr == None
#
#    def test_hello_world(self):
#        remote_object = dbus.SessionBus().get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus')
#        assert remote_object.hello_world() == 'Hello World!'
#


#class TestHamsterDBusServiceDBusMockStyle(dbusmock.DBusTestCase):
#    """
#    This is heavily inspired by the way ``dbusmock``does spawn its mock server.
#
#    This works!
#    """
#    @classmethod
#    def setuUpClass(klass):
#        klass.start_session_bus()
#        klass.dbus_con = klass.get_dbus()
#
#    def setUp(self):
#        import subprocess
#        import sys
#        import time
#        #self.service = hamster_dbus.HamsterDBusService()
#        env = os.environ.copy()
#    	self.deamon = subprocess.Popen([sys.executable, '-m', 'hamster_dbus.hamster_dbus', 'server'], env=env)
#        # Wait for the service to become available
#        #TestHamsterDBusServiceDBusMockStyle.wait_for_dbus_object(name, path, False)
#        time.sleep(2)
#        assert self.deamon.stdout == None
#        assert self.deamon.stderr == None
#
#    def test_hello_world(self):
#        remote_object = dbus.SessionBus().get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus') #        assert remote_object.hello_world() == 'Hello World!'
#

#class TestHamsterDBusServiceMu(dbusmock.DBusTestCase):
#    @classmethod
#    def setuUpClass(klass):
#        klass.start_session_bus()
#        klass.dbus_con = klass.get_dbus()
#
#    def setUp(self):
#        """Instead of the main loop our file we do this here."""
#        from multiprocessing import Process
#        import time
#        from dbus.mainloop.glib import DBusGMainLoop
#        from gi.repository import GLib, GObject
#
#        def run_server():
#            DBusGMainLoop(set_as_default=True)
#            self.loop = GLib.MainLoop()
#            myservice = hamster_dbus.HamsterDBusService(bus=self.dbus_con)
#            time.sleep(1)
#            self.loop.run()
#        self.p = Process(target=run_server)
#        self.p.start()
#
#    def tearDown(self):
#        self.loop.quit()
#
#    def test_hello_world(self):
#        remote_object = self.dbus_con.get_object('org.gnome.hamster_dbus', '/org/gnome/hamster_dbus')
#        assert remote_object.hello_world() == 'Hello World!'


# Pytest


def test_hello_world(hamster_interface):
    assert hamster_interface.hello_world() == 'Hello World!'

class TestGeneralMethods(object):
    """Make sure that genreal methods work as expected."""

    #@pytest.mark.xfail
    #def test_quit(self, hamster_service, hamster_interface):
    #    """Make sure that we actually shut down the service."""
    #    assert psutil.pid_exists(hamster_service.pid)
    #    hamster_interface.Quit()
    #    time.sleep(2)
    #    assert psutil.pid_exists(hamster_service.pid) is False

    def test_add_category_valid(self, hamster_interface):
        """Make sure that passing a valid string creates a new category and returns its pk."""
        result = hamster_interface.AddCategory('foobar')
        assert result >= 0

    def test_add_category_integer(self, hamster_interface):
        """Make sure that passing an integer returns error code."""
        result = hamster_interface.AddCategory(2)
        assert result == -1
