===============================
hamster-dbus
===============================

.. image:: https://img.shields.io/pypi/v/hamster-dbus.svg
        :target: https://pypi.python.org/pypi/hamster-dbus


.. image:: https://readthedocs.org/projects/hamster-dbus/badge/?version=latest
        :target: https://readthedocs.org/projects/hamster-dbus/?badge=latest
        :alt: Documentation Status


A dbus interface to ``hamster-lib``.

* Free software: GPL3
* Documentation: https://hamster-dbus.readthedocs.org.


Testing & Coverage
-------------------

The ``hamster-dbus`` project strives to provide maintainable, well documented and tested code.
To this end we do provide a basic test suite that is actively maintained and aims to provide >90%
coverage.
Unfortunately we currently lack the insight into glib/dbus best practices with
regards to testing and our current ``pytest`` based solution does only somewhat
work. The main problem is providing an isolated environment for actual unit
testing (not integration tests).
The way we handle things right now is by providing a dedicated fixture that launches a separate
session bus in a new process that our "objects to be tested" get hooked into.
While this works most of the time there are two practical issues here (besides not being proper unit tests):

1. You may see an error like this when running the test suite: ..

    [xcb] Unknown sequence number while processing queue
    [xcb] Most likely this is a multi-threaded client and XInitThreads has not been called
    [xcb] Aborting, sorry about that.

    Whilst we do not really understand whats going on this is most likely due to the fact that the
    new spawned session bus process is seperate from the actual main look.

2. ``coverage`` will report most of the "object" code as untested despite various tests executing
   their methods. This may be because those methods are "shadowed" by the ``@method`` decorator.
   Again, we lack the insight to deal with this right now.

So if you have any hints, pointers or even PRs that can help us improving our test setup we would
be most grateful! Until then we will not be able to automatically run the test suite on a CI server
which greatly limits our QA :(

To run the test suite locally, just execute the following within your virtualenv (after ``make develop``): ..

    make test


Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
