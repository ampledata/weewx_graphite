# installer for weewx_graphite
# Copyright 2014


from setup import ExtensionInstaller


def loader():
    return WeewxGraphiteInstaller()


class WeewxGraphiteInstaller(ExtensionInstaller):

    def __init__(self):
        super(WeewxGraphiteInstaller, self).__init__(
            version='0.0.3',
            name='graphite',
            description='Upload weather data to graphite.',
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
