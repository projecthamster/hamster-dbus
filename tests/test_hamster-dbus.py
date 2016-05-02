# -*- coding: utf-8 -*-

import pytest
import os
import dbus
import psutil
import time


import hamster_dbus.hamster_dbus as hamster_dbus



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
