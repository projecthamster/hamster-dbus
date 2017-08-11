===============================
hamster-dbus
===============================

A dbus interface to ``hamster-lib``.

* Free software: GPL3
* Documentation: https://hamster-dbus.readthedocs.org.


How to use
-----------

``hamster-dbus`` provides two very different but related functionalities.

1. ``hamster_dbus.objects`` provides several dbus object subclasses that can
   be used to export services over dbus that in effect expose ``hamster-lib``
   to over dbus.

2. ``hamster_dbus.storage`` contains ``DBusStore`` which can be used as a valid
   backend for ``hamster-lib`` that can communicate with the objects defined in
   ``hamster_dbus.objects``. This means any client that supports
   ``hamster-lib`` can use this backend (instead of the default SQLAlchemy one
   for example) to easily make their clients use an available dbus service
   instead of handling the backend functionality itself via SQLAlchemy.

These two aspects are independent of each other but are two opposing sides
(server and client of sorts) of the same medal.

On top of this, a primitive example dbus-service executeable
(``hamster_dbus_service.py``) has been included that can be used to get a
minimal hamster-dbus service running in no time.

Testing & Coverage
-------------------

The ``hamster-dbus`` project strives to provide maintainable, well documented
and tested code.  To this end we do provide a basic test suite that is actively
maintained and aims to provide >90% coverage.
Unfortunately we currently lack the insight into glib/dbus best practices with
regards to testing and our current ``pytest`` based solution does only somewhat
work. The main problem is providing an isolated environment for actual unit
testing (not integration tests).
The way we handle things right now is by providing a dedicated fixture that
launches a separate session bus in a new process that our "objects to be
tested" get hooked into.  While this works most of the time there are two
practical issues here (besides not being proper unit tests):

1. You may see an error like this when running the test suite::

    [xcb] Unknown sequence number while processing queue
    [xcb] Most likely this is a multi-threaded client and XInitThreads has not \
        been called
    [xcb] Aborting, sorry about that.

    Whilst we do not really understand whats going on this is most likely due
    to the fact that the new spawned session bus process is seperate from the
    actual main look.

2. ``coverage`` will report most of the "object" code as untested despite
   various tests executing their methods. This may be because those methods are
   "shadowed" by the ``@method`` decorator.  Again, we lack the insight to deal
   with this right now.

So if you have any hints, pointers or even PRs that can help us improving our
test setup we would be most grateful! Until then we will not be able to
automatically run the test suite on a CI server which greatly limits our QA :(

To run the test suite locally, just execute the following within your
virtualenv (after ``make develop``)::

    make test

Sidenote About Testing Signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
So far we have not managed to establish a proper way of testing signals.
In order to manually check if they are emitted as expected you may use the
following (``dbus-monitor`` needs to be installed)::

    dbus-monitor "type='signal',sender='org.projecthamster.HamsterDBus',interface='org.projecthamster.HamsterDBus1'"


Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
