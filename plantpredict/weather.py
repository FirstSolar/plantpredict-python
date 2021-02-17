import json
import requests
from plantpredict.plant_predict_entity import PlantPredictEntity
from plantpredict.error_handlers import handle_refused_connection, handle_error_response
from plantpredict.utilities import convert_json, camel_to_snake, snake_to_camel
from plantpredict.enumerations import EntityTypeEnum


class Weather(PlantPredictEntity):
    """
    The full contents of the Weather database entity (in JSON) can be found under
    "GET /Weather/{Id}" in `the general PlantPredict API documentation
    <http://app.plantpredict.com/swagger/ui/index#!/Weather/Weather_Get_0>`_.
    """
    def create(self):
        """
        POST /Weather

        Creates a new Weather entity.

        .. container:: toggle

            .. container:: header

                **Required Attributes**

            .. container:: required_attributes

                .. csv-table:: Minimum required attributes for successful Weather creation
                    :delim: ;
                    :header: Field, Type, Description
                    :stub-columns: 1

                    name; str; Name of weather file
                    country_code; str; Country code of the Weather's location (ex. US for United States, AUS for Australia, etc.) :py:meth:`plantpredict.Geo.get_location_info` will return this information.
                    country; str; Full name of the country of the Weather's location. :py:meth:`plantpredict.Geo.get_location_info` will return this information.
                    latitude; float; North-South coordinate of the Weather location (in decimal degrees).
                    longitude; float; East-West coordinate of the Weather location (in decimal degrees).
                    data_provider; int; Represents a weather data source. See (and/or import) :py:mod:`plantpredict.enumerations.WeatherDataProviderEnum` for a list of options.
                    weather_details; list of dict; The code block below contains an example of one timestamp (array element) of this field, as well as information on which dictionary keys are required.

                .. code-block:: python

                    weather_details[109] = {
                        "index": 110,                           # REQUIRED | is equal to the list index + 1
                        "time_stamp": "2018-01-01T1:00:00",     # REQUIRED
                        "global_horizontal_irradiance": 139.3,  # REQUIRED if no 'plane_of_array_irradiance' | [W/m^2]
                        "diffuse_horizontal_irradiance": 139.3, # [W/m^2]
                        "direct_normal_irradiance": 0.0,        # [W/m^2]
                        "beam_horizontal_irradiance": 0.0,      # [W/m^2]
                        "plane_of_array_irradiance": 100.0,     # REQUIRED if no 'global_horizontal_irradiance' | [W/m^2]
                        "temperature": 1.94,                    # REQUIRED | [degrees-Celsius]
                        "relative_humidity": 74.5,              # [%]
                        "precipitable_water": 2.0,              # [cm]
                        "soiling_loss": 0.19                    # [%]
                    }

        :return: A dictionary containing the weather id.
        :rtype: dict
        """
        self.create_url_suffix = "/Weather"
        return super(Weather, self).create()

    def delete(self):
        """
        DELETE /Weather/{WeatherId}

        Deletes an existing Weather entity in PlantPredict. The local instance of the Weather entity must have
        attribute self.id identical to the weather id of the Weather to be deleted.

        :return: A dictionary {"is_successful": True}.
        :rtype: dict
        """
        self.delete_url_suffix = "/Weather/{}".format(self.id)

        return super(Weather, self).delete()

    def get(self):
        """
        GET /Weather/{Id}

        Retrieves an existing Weather entity in PlantPredict and automatically assigns all of its attributes to the
        local Weather object instance. The local instance of the Weather entity must have attribute self.id identical
        to the weather id of the Weather to be retrieved.

        :return: A dictionary containing all of the retrieved Weather attributes.
        :rtype: dict
        """
        self.get_url_suffix = "/Weather/{}".format(self.id)
        return super(Weather, self).get()

    def update(self):
        """
        PUT /Weather

        Updates an existing Weather entity in PlantPredict using the full attributes of the local Weather object instance.
        Calling this method is most commonly preceded by instantiating a local instance of Weather with a specified
        weather id, calling the Weather.get() method, and changing any attributes locally.

        The required fields are identical to those of :py:meth:`plantpredict.weather.create` with the addition of:
        .. csv-table:: Minimum required attributes for successful Weather creation
            :delim: ;
            :header: Field; Type; Description
            :stub-columns: 1

            id; int; Unique identifier of existing Weather entity.


        :return: A dictionary {"is_successful": True}.
        :rtype: dict
        """
        self.update_url_suffix = "/Weather"
        return super(Weather, self).update()

    @handle_refused_connection
    @handle_error_response
    def get_details(self):
        """
        GET /Weather/{Id}/Detail

        Returns detailed time series of Weather entity.

        :returns: A list of dictionaries where each dictionary contains one timestamp of detailed weather data.
        :rtype: list of dicts
        """
        return requests.get(
            url=self.api.base_url + "/Weather/{}/Detail".format(self.id),
            headers={"Authorization": "Bearer " + self.api.access_token}
        )

    @handle_refused_connection
    @handle_error_response
    def search(self, latitude, longitude, search_radius=1):
        """
        GET /Weather/Search

        Searches for all existing Weather entities within a search radius of a specified latitude/longitude.

        :param latitude: North-South coordinate of the Weather location, in decimal degrees.
        :type latitude: float
        :param longitude: East-West coordinate of the Project location, in decimal degrees.
        :type longitude: float
        :param search_radius: search radius in miles
        :type search_radius: float
        :return: #TODO
        :rtype: list of dicts
        """

        response = requests.get(
            url=self.api.base_url + "/Weather/Search",
            headers={"Authorization": "Bearer " + self.api.access_token},
            params=convert_json({
                'latitude': latitude,
                'longitude': longitude,
                'search_radius': search_radius
            }, snake_to_camel)
        )

        weather_list = json.loads(response.content)

        return [convert_json(w, camel_to_snake) for w in weather_list]

    @handle_refused_connection
    @handle_error_response
    def download(self, latitude, longitude, provider=0):
        """
        POST /Weather/Download/{Provider}

        :param latitude:
        :type latitude: float
        :param longitude:
        :type longitude: float
        :param provider: Represents a weather data source. See (and/or import) :py:mod:`plantpredict.enumerations.WeatherSourceTypeAPIEnum` for a list of options.
        :type provider: int
        :return: #TODO
        :rtype: dict
        """
        response = requests.post(
            url=self.api.base_url + "/Weather/Download/{}".format(provider),
            headers={"Authorization": "Bearer " + self.api.access_token},
            params={'latitude': latitude, 'longitude': longitude}
        )

        self.id = json.loads(response.content)['id'] if 200 <= response.status_code < 300 else None

        return response

        @handle_refused_connection
    @handle_error_response
    def change_status(self, new_status, note=""):
        """
        POST /Weather/Status

        Change the status (and resulting sharing/privacy settings) of a weather file (ex. from py:attr:`DRAFT_PRIVATE` to
        py:attr:`DRAFT-SHARED`.

        :param int new_status: Enumeration representing status to change weather to. See (or import)
                               :py:class:`plantpredict.enumerations.LibraryStatusEnum`.
        :param str note: Description of reason for change.
        :return:
        """
        return requests.post(
            url=self.api.base_url + "/Weather/Status",
            headers={"Authorization": "Bearer " + self.api.access_token},
            json=[{
                "name": self.name,
                "id": self.id,
                "type": EntityTypeEnum.WEATHER,
                "status": new_status,
                "note": note
            }]
        )
