#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Packing metadata for setuptools."""


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'future',
    'hamster_lib',
]

setup(
    name='hamster-dbus',
    version='0.10.0',
    description="A dbus interface to hamster-lib.",
    long_description=readme + '\n\n' + history,
    author="Eric Goller",
    author_email='eric.goller@ninjaduck.solutions',
    url='https://github.com/elbenfreund/hamster-dbus',
    packages=[
        'hamster_dbus',
    ],
    package_dir={'hamster_dbus':
                 'hamster_dbus'},
    package_data={'hamster-dbus': ['examples/*']},
    install_requires=requirements,
    entry_points={
        'console_scripts': ['hamster-dbus-service = hamster_dbus.hamster_dbus_service:_main']
    },
    license="GPL3",
    zip_safe=False,
    keywords='hamster-dbus',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
