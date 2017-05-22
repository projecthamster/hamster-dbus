#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Provide a trivial service implementation to export ``hamster-lib`` functionality."""

# This file is part of 'hamster-dbus'.
#
# 'hamster-dbus' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-dbus' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  'hamster-dbus'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import datetime
import sys

import hamster_lib
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from hamster_dbus import objects


def _get_config():
    """
    Get config to be passed to controller.

    Attention! You need to adjust these values to you own needs! In particular
    ``db_path`` is something you most likly do not want. If you keep it as is
    all changes will be lost on reboot!
    """
    return {
        'store': 'sqlalchemy',
        'day_start': datetime.time(5, 30, 0),
        'fact_min_delta': 60,
        'tmpfile_path': '/tmp/tmpfile.pickle',
        'db_engine': 'sqlite',
        'db_path': ':memory:',
    }


def _main():
    controller = hamster_lib.HamsterControl(_get_config())
    DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()
    main_object = objects.HamsterDBus(loop)
    objects.CategoryManager(controller, main_object)
    objects.ActivityManager(controller, main_object)
    objects.TagManager(controller, main_object)
    objects.FactManager(controller, main_object)
    # Run needs to be called after we setup our service
    loop.run()


if __name__ == '__main__':
    arg = ""
    if len(sys.argv) > 1:
        # truncate args
        arg = sys.argv[1]

    if arg == "server":
        _main()
