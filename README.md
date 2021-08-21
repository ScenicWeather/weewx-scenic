# weewx-nowdawn

![Windows Build Status](https://github.com/Now-Dawn/weewx-nowdawn/workflows/Windows/badge.svg)
![Linux Build Status](https://github.com/Now-Dawn/weewx-nowdawn/workflows/Linux/badge.svg)
![MIT License](https://img.shields.io/github/license/Now-dawn/weewx-nowdawn)

# Driver for integrating WeeWx supported weather stations with the NowDawn weather station API

## Installation

1. Get an API key

Register for an API key at [https://stations.nowdawn.com](https://stations.nowdawn.com)

1. Download

`wget -O weewx-nowdawn.zip https://github.com/Now-Dawn/weewx-nowdawn/archive/master.zip`

1. Run the installer

`wee_extension --install weewx-nowdawn.zip`

1. Enter parameters in the WeeWx configuration file

`[StdRESTful]
    [[NowDawn]]
        api_key = API_KEY`

1. Restart WeeWx

`sudo /etc/init.d/weewx stop`
`sudo /etc/init.d/weewx start`
