# Copyright 2020 NowDawn

"""
This weewx extension uploads data to a http://stations.nowdawn.com

The protocol is described at the nowdawn blog:

https://community.windy.com/topic/8168/report-you-weather-station-data-to-windy

Minimal configuration

[StdRESTful]
    [[NowDawn]]
        api_key = API_KEY

When using multiple stations, distinguish them using a station identifier.
For example:

[StdRESTful]
    [[NowDawn]]
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
DEFAULT_URL = 'https://stations.nowdawn.com'
REQUIRED_WEEWX = "4.0.0"

if StrictVersion(__version__) < StrictVersion(REQUIRED_WEEWX):
    raise UnsupportedFeature("weewx %s or greater is required, found %s"
                                   % (REQUIRED_WEEWX, __version__))

LOG = getLogger(__name__)

def info(msg):
    """"""
    LOG.info(msg)

class NowDawn(StdRESTbase):
    """"""

    def __init__(self, engine, cfg_dict):
        super(NowDawn, self).__init__(engine, cfg_dict)
        info("version is %s" % VERSION)
        site_dict = get_site_dict(cfg_dict, 'NowDawn', 'api_key')
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


class NowDawnThread(RESTThread):
    """"""
    def __init__(self, q, api_key, station=0, skip_upload=False,
                 manager_dict=None, post_interval=None, max_backlog=maxsize,
                 stale=None, log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(NowDawnThread, self).__init__(q, protocol_name='NowDawn',
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
        self.station = to_int(station)
        self.server_url = DEFAULT_URL
        info("Data will be uploaded to %s" % self.server_url)
        self.skip_upload = to_bool(skip_upload)

    def format_url(self, _):
        """Return an URL for doing a POST to NowDawn"""
        return '%s/%s' % (DEFAULT_URL, self.api_key)

    def get_post_body(self, record):
        """Send a POST request to NowDawn server"""
        record_m = to_METRICWX(record)
        data = {
            'station': self.station,  # integer identifier, usually "0"
            'dateutc': time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.gmtime(record_m['dateTime']))
            }
        if 'outTemp' in record_m:
            data['temp'] = record_m['outTemp']  # degree_C
        if 'windSpeed' in record_m:
            data['wind'] = record_m['windSpeed']  # m/s
        if 'windDir' in record_m:
            data['winddir'] = record_m['windDir']  # degree
        if 'windGust' in record_m:
            data['gust'] = record_m['windGust']  # m/s
        if 'outHumidity' in record_m:
            data['rh'] = record_m['outHumidity']  # percent
        if 'dewpoint' in record_m:
            data['dewpoint'] = record_m['dewpoint']  # degree_C
        if 'barometer' in record_m:
            if record_m['barometer'] is not None:
                data['pressure'] = 100.0 * record_m['barometer']  # Pascals
            else:
                data['pressure'] = None
        if 'hourRain' in record_m:
            data['precip'] = record_m['hourRain']  # mm in past hour
        if 'UV' in record_m:
            data['uv'] = record_m['UV']

        body = {
            'observations': [data]
        }

        return dumps(body), 'application/json'


# Use this hook to test the uploader:
#   PYTHONPATH=bin python bin/user/nowdawn.py

if __name__ == "__main__":
    setup('nowdawn', {})
    QUEUE = Queue()
    THREAD = NowDawnThread(QUEUE, api_key='ABC123', station=0)
    THREAD.start()
    RESPONSE = {'dateTime': int(time.time() + 0.5),
                'usUnits': US, 'outTemp': 32.5, 'inTemp': 75.8,
                'humidity': 24, 'wind_speed': 10, 'wind_direction': 32}
    print(THREAD.format_url(RESPONSE))
    QUEUE.put(RESPONSE)
    QUEUE.put(None)
    THREAD.join(30)
