#!/usr/bin/env python

"""
Sends weewx weather records to Graphite using the Carbon/TCP protocol.
"""


import Queue
import socket
import sys
import syslog

import weewx
import weewx.restx

from weeutil.weeutil import to_bool


class Graphite(weewx.restx.StdRESTful):
    """
    Sends weewx weather records to Graphite using the Carbon/TCP protocol.
    """

    def __init__(self, engine, config_dict):
        super(Graphite, self).__init__(engine, config_dict)
        try:
            site_dict = weewx.restx.get_dict(config_dict, 'Graphite')
            site_dict['host']
            site_dict['port']
        except KeyError, e:
            syslog.syslog(
                syslog.LOG_DEBUG, "restx: Graphite: "
                "Data will not be posted: Missing option %s" % e
            )
            return

        site_dict.setdefault(
            'database_dict',
            config_dict['Databases'][config_dict['StdArchive']['archive_database']]
        )

        self.archive_queue = Queue.Queue()
        self.archive_thread = GraphiteThread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        syslog.syslog(
            syslog.LOG_INFO,
            "restx: Graphite: Data will be sent to host %s:%s" %
            (site_dict['host'], site_dict['port'])
        )

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)


class GraphiteThread(weewx.restx.RESTThread):

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = '2003'
    DEFAULT_PREFIX = 'weewx'

    def __init__(self, queue, database_dict,
                  host=DEFAULT_HOST, port=DEFAULT_PORT, prefix=DEFAULT_PREFIX,
                  skip_upload=False, post_interval=300, max_backlog=sys.maxint,
                  stale=None, log_success=True, log_failure=True,
                  timeout=60, max_tries=3, retry_wait=5):

        """Initialize an instances of GraphiteThread.

        :param host: Graphite Carbon Host.
        :param port: Graphite Carbon Port.
        :param prefix: Graphite Queue Prefix.

        Optional parameters:

        log_success: If True, log a successful post in the system log.
        Default is True.

        log_failure: If True, log an unsuccessful post in the system log.
        Default is True.

        max_backlog: How many records are allowed to accumulate in the queue
        before the queue is trimmed.
        Default is sys.maxint (essentially, allow any number).

        max_tries: How many times to try the post before giving up.
        Default is 3

        stale: How old a record can be and still considered useful.
        Default is None (never becomes too old).

        post_interval: The interval in seconds between posts.
        xxx requests that uploads happen no more often than 5 minutes, so
        this should be set to no less than 300.
        Default is 300

        timeout: How long to wait for the server to respond before giving up.
        Default is 60 seconds

        skip_upload: debugging option to display data but do not upload
        Default is False
        """
        super(GraphiteThread, self).__init__(
            queue,
            protocol_name='Graphite',
            database_dict=database_dict,
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
        self.skip_upload = to_bool(skip_upload)

    def collect_metric(self, name, value, timestamp):
        if self.prefix:
            metric_name = '.'.join([self.prefix, name])
        else:
            metric_name = name

        syslog.syslog(
            syslog.LOG_DEBUG, "restx: Graphite: %s" % locals()
        )

        sock = socket.socket()
        sock.connect((self.host, self.port))
        sock.send("%s %d %d\n" % (metric_name, value, timestamp))
        sock.close()

    def get_record(self, record, archive):
        # Get the record from my superclass
        return super(GraphiteThread, self).get_record(record, archive)

    def process_record(self, record, archive):
        if self.skip_upload:
            syslog.syslog(
                syslog.LOG_DEBUG,
                "restx: Graphite: skip_upload=True, skipping upload"
            )
        else:
            for k,v in record.iteritems():
                self.collect_metric(k, v, record['dateTime'])


#
# Record format:
#
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
