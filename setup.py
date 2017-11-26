#!/usr/bin/env python

from setuptools import setup

setup(
    name='autodesk',
    version='1.0',
    packages=['autodesk'],
    include_package_data=True,
    install_requires=['flask', 'RPi.GPIO', 'nanomsg', 'msgpack-python'],
    test_suite='tests',
    scripts=['bin/logger.py'],
)
