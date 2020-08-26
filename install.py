# Installer for NowDawn
# Copyright 2020 NowDawn
# Distributed under the MIT License

from weecfg.extension import ExtensionInstaller

def loader():
    """"""
    return NowDawnInstaller()

class NowDawnInstaller(ExtensionInstaller):
    def __init__(self):
        super(NowDawnInstaller, self).__init__(
            version="0.1",
            name='nowdawn',
            description='Upload weather data to NowDawn.',
            author="Conor Forde",
            author_email="contact@nowdawn.com",
            restful_services='user.nowdawn.NowDawn',
            config={
                'StdRESTful': {
                    'NowDawn': {
                        'api_key': 'replace_me'}}},
            files=[('bin/user', ['bin/user/nowdawn.py'])]
            )
