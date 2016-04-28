# -*- coding: utf-8 -*-

import pytest
import dbusmock
import os
import dbus
import subprocess
from multiprocessing import Process
import time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib, GObject
from threading import Thread
#from dbus import GTestDBus


import hamster_dbus.hamster_dbus as hamster_dbus


class TestHamsterDBusService(dbusmock.DBusTestCase):
    @classmethod
    def setuUpClass(klass):
        klass.start_session_bus()
        klass.dbus_con = klass.get_dbus()

    def setUp(self):
        #self.service = hamster_dbus.HamsterDBusService()
        env = os.environ.copy()
    	self.p = subprocess.Popen(['python', 'hamster_dbus/hamster_dbus.py', 'server'], env=env)
        # Wait for the service to become available
        time.sleep(1)
        assert self.p.stdout == None
        assert self.p.stderr == None
        pass

    def test_foo(self):
        #print(self.service)
        remote_object = dbus.SessionBus().get_object('org.gnome.hamster_dbus', '/fo')
        print(remote_object)
        print(self.get_dbus())
        print(dbus.SessionBus())
        #assert id(self.service) == id(dbus.SessionBud)
