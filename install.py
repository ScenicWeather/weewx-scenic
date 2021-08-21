# Installer for Scenic Weather
# Copyright 2021 Scenic Weather
# Distributed under the MIT License

from weecfg.extension import ExtensionInstaller

def loader():
    """"""
    return ScenicInstaller()

class ScenicInstaller(ExtensionInstaller):
    def __init__(self):
        super(ScenicInstaller, self).__init__(
            version="0.2",
            name='scenic',
            description='Upload weather data to Scenic Weather.',
            author="Conor Forde",
            author_email="contact@scenicdata.com",
            restful_services='user.scenicdata.Scenic',
            config={
                'StdRESTful': {
                    'Scenic': {
                        'api_key': 'replace_me'}}},
            files=[('bin/user', ['bin/user/scenic.py'])]
        )
