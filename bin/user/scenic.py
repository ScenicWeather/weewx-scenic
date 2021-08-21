# Copyright 2021 Scenic Weather

"""
This weewx extension uploads data to a http://api.scenicdata.com/station

The protocol is described at the scenic weather blog:

https://community.windy.com/topic/8168/report-you-weather-station-data-to-windy

Minimal configuration

[StdRESTful]
    [[Scenic]]
        api_key = API_KEY

When using multiple stations, distinguish them using a station identifier.
For example:

[StdRESTful]
    [[Scenic]]
        api_key = API_KEY
        station = 1

The default station identifier is 0.
"""

from queue import Queue
from distutils.version import StrictVersion
from json import dumps
from sys import maxsize
import time
from logging import getLogger
from weewx import NEW_ARCHIVE_RECORD, UnknownBinding, UnsupportedFeature
from weewx import __version__, US
from weewx.manager import get_manager_dict_from_config
from weewx.restx import get_site_dict, StdRESTbase, RESTThread
from weewx.units import to_METRICWX
from weeutil.weeutil import to_bool, to_int
from weeutil.logger import setup

VERSION = "0.1"
DEFAULT_URL = "https://api.scenicdata.com/station/%s/key/%s"

REQUIRED_WEEWX = "4.0.0"

if StrictVersion(__version__) < StrictVersion(REQUIRED_WEEWX):
    raise UnsupportedFeature("weewx %s or greater is required, found %s"
                             % (REQUIRED_WEEWX, __version__))

LOG = getLogger(__name__)

def info(msg):
    """"""
    LOG.info(msg)

def get_value(record, key):
    """"""
    if None in (record, key):
        return None

    if key in record:
        return record[key]

    return None

class Scenic(StdRESTbase):
    """"""

    def __init__(self, engine, cfg_dict):
        super(Scenic, self).__init__(engine, cfg_dict)
        info("version is %s" % VERSION)
        site_dict = get_site_dict(cfg_dict, 'Scenic', 'api_key')
        if site_dict is None:
            return

        try:
            site_dict['manager_dict'] = get_manager_dict_from_config(cfg_dict,
                                                                     'wx_binding')
        except UnknownBinding:
            pass

        self.archive_queue = Queue()
        self.archive_thread = NowDawnThread(self.archive_queue, **site_dict)

        self.archive_thread.start()
        self.bind(NEW_ARCHIVE_RECORD, self.new_archive_record)

    def new_archive_record(self, event):
        """"""
        self.archive_queue.put(event.record)


class ScenicThread(RESTThread):
    """"""
    def __init__(self, q, api_key, station=0, skip_upload=False,
                 manager_dict=None, post_interval=None, max_backlog=maxsize,
                 stale=None, log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(ScenicThread, self).__init__(q, protocol_name='Scenic',
                                            manager_dict=manager_dict,
                                            post_interval=post_interval,
                                            max_backlog=max_backlog,
                                            stale=stale,
                                            log_success=log_success,
                                            log_failure=log_failure,
                                            max_tries=max_tries,
                                            timeout=timeout,
                                            retry_wait=retry_wait)
        self.api_key = api_key
        self.station = to_int(station) # TODO conver to alpha numeric
        self.server_url = DEFAULT_URL % (station, api)
        info("Data will be uploaded to %s" % self.server_url)
        self.skip_upload = to_bool(skip_upload)

    def format_url(self, _):
        """Return an URL for doing a POST to Scenic"""
        return DEFAULT_URL % (station, api_key)

    def get_post_body(self, record):
        """Send a POST request to Scenic server"""
        record_m = to_METRICWX(record)
        data = {
            'station': self.station,  # integer identifier, usually "0"
            'dateutc': time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.gmtime(record_m['dateTime']))
        }
        data['temperature'] = get_value(record_m, 'outTemp')  # degree_C
        data['wind_speed'] = get_value(record_m, 'windSpeed')  # m/s
        data['wind_direction'] = get_value(record_m, 'windDir')  # degree
        data['gust'] = get_value(record_m, 'windGust')  # m/s
        data['humidity'] = get_value(record_m, 'outHumidity')  # percent
        data['dewpoint'] = get_value(record_m, 'dewpoint')  # degree_C
        barometric = get_value(record_m, 'barometer')
        if barometric is None:
            data['pressure'] = None
        else:
            data['pressure'] = 100.0 * barometric  # Pascals

        data['hour_rain'] = get_value(record_m, 'hourRain')  # mm in past hour
        data['ultraviolet'] = get_value(record_m, 'UV')

        body = {
            'observations': [data]
        }

        return dumps(body), 'application/json'


# Use this hook to test the uploader:
#   PYTHONPATH=bin python bin/user/scenic.py

if __name__ == "__main__":
    setup('scenic', {})

    QUEUE = Queue()
    THREAD = ScenicThread(QUEUE, api_key='ABC123', station=0)
    THREAD.start()
    RESPONSE = {'dateTime': int(time.time() + 0.5),
                'usUnits': US, 'outTemp': 32.5, 'inTemp': 75.8,
                'humidity': 24, 'wind_speed': 10, 'wind_direction': 32}
    print(THREAD.format_url(RESPONSE))
    QUEUE.put(RESPONSE)
    QUEUE.put(None)
    THREAD.join(30)
