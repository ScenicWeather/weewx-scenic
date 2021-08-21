# weewx-scenic

![Windows Build Status](https://github.com/ScenicWeather/weewx-scenic/workflows/Windows/badge.svg)
![Linux Build Status](https://github.com/ScenicWeather/weewx-scenic/workflows/Linux/badge.svg)
![MIT License](https://img.shields.io/github/license/ScenicWeather/weewx-scenic)

# Driver for integrating WeeWx supported weather stations with the Scenic Weather weather station API

## Installation

1. Get an API key

Register for an API key at [https://stations.scenicdata.com](https://stations.scenicdata.com)

1. Download

`wget -O weewx-scenic.zip https://github.com/ScenicWeather/weewx-scenic/archive/master.zip`

1. Run the installer

`wee_extension --install weewx-scenic.zip`

1. Enter parameters in the WeeWx configuration file

`[StdRESTful]
    [[Scenic]]
        api_key = API_KEY`

1. Restart WeeWx

`sudo /etc/init.d/weewx stop`
`sudo /etc/init.d/weewx start`
