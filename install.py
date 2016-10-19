#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for WeeWX Graphite Extension.

Source:: https://github.com/ampledata/weewx_graphite
"""


__title__ = 'graphite'
__version__ = '2.0.0'
__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


import setup


def loader():
    """Installs WeeWX Graphite Extension."""
    return WeewxGraphiteInstaller()


class WeewxGraphiteInstaller(setup.ExtensionInstaller):
    """Installs WeeWX Graphite Extension."""

    def __init__(self):
        super(WeewxGraphiteInstaller, self).__init__(
            version=__version__,
            name=__title__,
            description='Send weather data to graphite.',
            author='Greg Albrecht W2GMD',
            author_email='oss@undef.net',
            restful_services='user.graphite.Graphite',
            config={
                'StdRESTful': {
                    'Graphite': {
                        'host': 'CARBON_HOST',
                        'port': 'CARBON_PORT'
                    }
                }
            },
            files=[('bin/user', ['bin/user/graphite.py'])]
        )
