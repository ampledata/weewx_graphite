#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sends WeeWX weather records to Graphite using the Carbon/TCP protocol.

Source:: https://github.com/ampledata/weewx_graphite

Reference WeeWX Record format:
# {
#   'daily_rain': 0.0,
#   'wind_average': 3.5007240370967794,
#   'outHumidity': 83.62903225806451,
#   'heatindex': 61.59999999999994,
#   'day_of_year': 36.0,
#   'inTemp': 61.59999999999994,
#   'windGustDir': 200.470488,
#   'barometer': 30.238869061178168,
#   'windchill': 61.59999999999994,
#   'dewpoint': 56.59074077611711,
#   'rain': 0.0,
#   'pressure': 30.076167509542763,
#   'long_term_rain': 1.900000000000002,
#   'minute_of_day': 1348.0,
#   'altimeter': 30.230564691725238,
#   'usUnits': 1,
#   'interval': 5,
#   'dateTime': 1417218600.0,
#   'windDir': 187.7616636785259,
#   'outTemp': 61.59999999999994,
#   'windSpeed': 3.804394058064512,
#   'inHumidity': 83.62903225806451,
#   'windGust': 6.21371
# }
#
"""


__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


import Queue
import socket
import sys
import syslog

import weewx
import weewx.restx
import weeutil.weeutil


class Graphite(weewx.restx.StdRESTful):
    """
    Sends WeeWX weather records to Graphite using the Carbon/TCP protocol.
    """

    def __init__(self, engine, config_dict):
        super(Graphite, self).__init__(engine, config_dict)
        try:
            _graphite_dict = weeutil.weeutil.accumulateLeaves(
                config_dict['StdRESTful']['Graphite'], max_level=1)
        except KeyError as exc:
            syslog.syslog(
                syslog.LOG_DEBUG, "restx: Graphite: "
                "Data will not be posted: Missing option %s" % exc
            )
            return

        _manager_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'],
            config_dict['Databases'],
            'wx_binding'
        )

        self.archive_queue = Queue.Queue()
        self.archive_thread = GraphiteThread(
            self.archive_queue,
            _manager_dict,
             **_graphite_dict
        )
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        syslog.syslog(
            syslog.LOG_INFO,
            "restx: Graphite: Data will be sent to host %s:%s" %
            (_graphite_dict['host'], _graphite_dict['port'])
        )

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)


class GraphiteThread(weewx.restx.RESTThread):

    """
    Thread for sending WeeWX Weather Data to Graphite.
    """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = '2003'
    DEFAULT_PREFIX = 'weewx'
    DEFAULT_POST_INTERVAL = 300
    DEFAULT_TIMEOUT = 60
    DEFAULT_MAX_TRIES = 3
    DEFAULT_RETRY_WAIT = 5

    def __init__(self, queue, manager_dict,
                 host=DEFAULT_HOST, port=DEFAULT_PORT, prefix=DEFAULT_PREFIX,
                 skip_upload=False, post_interval=DEFAULT_POST_INTERVAL,
                 max_backlog=sys.maxint, stale=None, log_success=True,
                 log_failure=True, timeout=DEFAULT_TIMEOUT,
                 max_tries=DEFAULT_MAX_TRIES, retry_wait=DEFAULT_RETRY_WAIT):

        """Initialize an instances of GraphiteThread.

        :param host: Graphite Carbon Host.
        :param port: Graphite Carbon Port.
        :param prefix: Graphite Queue Prefix.
        :param log_success: Log a successful post in the system log.
        :param log_failure: Log an unsuccessful post in the system log.
        :param max_backlog: Max length of Queue before trimming. dft=sys.maxint
        :param max_tries: How many times to try the post before giving up.
        :param stale: How old a record can be and still considered useful.
        :param post_interval: The interval in seconds between posts.
        :param timeout: How long to wait for the server to respond before fail.
        :param skip_upload: Debugging option to display data but do not upload.
        """
        super(GraphiteThread, self).__init__(
            queue,
            protocol_name='Graphite',
            manager_dict=manager_dict,
            post_interval=post_interval,
            max_backlog=max_backlog,
            stale=stale,
            log_success=log_success,
            log_failure=log_failure,
            timeout=timeout,
            max_tries=max_tries,
            retry_wait=retry_wait
        )

        self.host = host
        self.port = port
        self.prefix = prefix
        self.skip_upload = weeutil.weeutil.to_bool(skip_upload)

    def collect_metric(self, name, value, timestamp):
        if self.prefix:
            metric_name = '.'.join([self.prefix, name])
        else:
            metric_name = name

        if value is None:
            _value = 0.0
        else:
            _value = value

        sock = socket.socket()
        sock.connect((self.host, int(self.port)))
        sock.send("%s %f %d\n" % (metric_name, _value, timestamp))
        sock.close()

    def process_record(self, record, dbmanager):
        _ = dbmanager

        if self.skip_upload:
            syslog.syslog(
                syslog.LOG_DEBUG,
                "restx: Graphite: skip_upload=True, skipping upload"
            )
        else:
            for rkey, rval in record.iteritems():
                self.collect_metric(rkey, rval, record['dateTime'])
