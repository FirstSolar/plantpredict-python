import requests
from plantpredict import settings
from plantpredict.error_handlers import handle_refused_connection, handle_error_response


class Geo(object):
    """
    This API resource does not represent a database entity in PlantPredict. This is a simplified connection to the
    Google Maps API. See Google Maps API Reference for further functionality. (https://developers.google.com/maps/)
    """

    @staticmethod
    @handle_error_response
    @handle_refused_connection
    def get_location_info(latitude, longitude):
        """GET /Geo/{Latitude}/{Longitude}/Location

        :param latitude:
        :param longitude:
        :return: Example response -
            {
                u'country': u'United States',
                u'country_code': u'US',
                u'locality': u'San Francisco',
                u'region': u'North America',
                u'state_province': u'California',
                u'state_province_code': u'CA'
            }
        """
        return requests.get(
            url=settings.BASE_URL + "/Geo/{}/{}/Location".format(latitude, longitude),
            headers={"Authorization": "Bearer " + settings.TOKEN}
        )

    @staticmethod
    @handle_error_response
    @handle_refused_connection
    def get_elevation(latitude, longitude):
        """GET /Geo/{Latitude}/{Longitude}/Elevation

        :param latitude:
        :param longitude:
        :return: Example response -
            {
                u'elevation': 100.0
            }
        """
        return requests.get(
            url=settings.BASE_URL + "/Geo/{}/{}/Elevation".format(latitude, longitude),
            headers={"Authorization": "Bearer " + settings.TOKEN}
        )

    @staticmethod
    @handle_error_response
    @handle_refused_connection
    def get_timezone(latitude, longitude):
        """GET /Geo/{Latitude}/{Longitude}/TimeZone

        :param latitude:
        :param longitude:
        :return: Example response -
            {
                u'timeZone': -8.0
            }
        """
        return requests.get(
            url=settings.BASE_URL + "/Geo/{}/{}/TimeZone".format(latitude, longitude),
            headers={"Authorization": "Bearer " + settings.TOKEN}
        )

    def __init__(self):
        pass
