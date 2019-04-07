#!/usr/bin/env python

from setuptools import setup

setup(
    name='autodesk',
    version='1.0',
    packages=['autodesk', 'autodesk.hardware'],
    install_requires=[
        'aiohttp',
        'aiohttp_jinja2',
        'matplotlib',
        'numpy',
        'pandas',
        'pyyaml'
    ],
    package_data={
        'autodesk': [
            'templates/*.*'
        ]
    },
    include_package_data=True,
)
