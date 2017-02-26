Packaging
=========

``{{ cookiecutter.project_name }}`` follows the `semantic versioning
<https://semver.org>`_ scheme.  Each release is packaged and uploaded to `pypi
<https://pypi.python.org/pypi/{{ cookiecutter.project_slug }}>`_.  We provide a
compliant ``setup.py`` which contains all the meta information relevant to
users of ``{{ cookiecutter.project_name }}``. If you stumble upon any
incompatibilities or dependency issue please let us know.  If you are
interested in packaging ``{{ cookiecutter.project_name }}`` for your preferred
distribution or in some other context we would love to hear from you!


About requirements/\*.pip
-------------------------
We do fully follow Donald Stuffts `argument
<https://caremad.io/2013/07/setup-vs-requirement/>`_ that information given
``setup.py`` is of fundamentally different nature than what may be located
under ``requirements/*.pip`` (Additional comments can be found in the
`packaging guide
<http://python-packaging-user-guide.readthedocs.org/en/latest/requirements/>`_
and with `Hynek Schlawack
<https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/>`_).
As far as packaging goes ``setup.py`` is authoritative. We provide a set of
specific environments under ``requirements/*`` that mainly developers and 3rd
parties may find useful. This way we can easily enable contributers to get a
suitable ``virtualenv`` running or specify our test environment in one central
location.  If for example you wanted to package ``{{ cookiecutter.project_name
}}`` for ``debian-stable``, it would be mighty convenient to just provide
another requirements.txt with all the relevant dependencies pinned to what your
target distro would provide. Now you can run the entire test suit against a
reliable representation of said target system.
