# weewx-nowdawn

### Driver for integrating WeeWx supported weather stations with the NowDawn weather station API

## Installation

1. Get an API key

Register for an API key at [stations.nowdawn.com](https://stations.nowdawn.com)

1. Download

`wget -O weewx-nowdawn.zip https://github.com/Now-Dawn/weewx-nowdawn/archive/master.zip`

1. Run the installer

`wee_extension --install weewx-nowdawn.zip`

1. Enter parameters in the weewx configuration file

```[StdRESTful]
    [[NowDawn]]
        api_key = API_KEY```

1. Restart weewx

`sudo /etc/init.d/weewx stop`
`sudo /etc/init.d/weewx start`
