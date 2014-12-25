#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for WeeWX Graphite Extension.

Source:: https://github.com/ampledata/weewx_graphite
"""


__title__ = 'graphite'
__version__ = '1.0.0'
__author__ = 'Greg Albrecht <gba@onbeep.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2014 OnBeep, Inc.'


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
            author='Greg Albrecht',
            author_email='gba@onbeep.com',
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
