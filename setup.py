#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "autopulse",
    version = "1.0.1",
    packages = find_packages('src'),
    package_dir = { '': 'src'},
    author = "Naftuli Kay",
    author_email = "me@naftuli.wtf",
    url = "https://github.com/naftulikay/autopulse",
    install_requires = [
        'setuptools',
        'pulsectl',
        'pyyaml',
    ],
    dependency_links = [],
    entry_points = {
        'console_scripts': [
            'autopulse = autopulse:main'
        ]
    }
)
