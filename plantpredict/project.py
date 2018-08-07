import requests
import json
from plantpredict import settings
from plantpredict.plant_predict_entity import PlantPredictEntity
from plantpredict.error_handlers import handle_refused_connection, handle_error_response
from plantpredict.utilities import convert_json, camel_to_snake


class Project(PlantPredictEntity):
    """
    The full contents of the Project database entity (in JSON) can be found under "GET /Project/{Id}" in `the general
    PlantPredict API documentation <http://app.plantpredict.com/swagger/ui/index#!/Project/Project_Get_0>`_.
    """

    def create(self, name=None, latitude=None, longitude=None, country=None, country_code=None, elevation=None,
               standard_offset_from_utc=None):
        """HTTP Request: POST /Project

        Creates a new Project entity in PlantPredict and assigns the uid of the newly created Project` to self.id in
        the local object instance. Any attributes (including but not limited to those also assignable via the inputs to
        this method) assigned prior to calling this method will be recorded in the new Project entity in PlantPredict.
        The input variables to this method are those required for successful Project creation.

        The following variables can be obtained via the methods belonging to plantpredict.Geo: country
        and country_code (plantpredict.Geo.get_location_info), elevation (plantpredict.Geo.get_elevation), and
        standard_offset_from_utc (plantpredict.Geo.get_timezone).

        :param name: The name of the Project.
        :type name: str
        :param latitude: North-South coordinate of the Project location, in decimal degrees.
        :type latitude: float
        :param longitude: East-West coordinate of the Project location, in decimal degrees.
        :type longitude: float
        :param country: Full name of the country of the Project's location.
        :type country: str
        :param country_code: Country code of the Project's location (ex. US for United States, AUS for Australia, etc.)
        :type country_code: str
        :param elevation: The elevation of the Project location above sea level in units meters.
        :type elevation: float
        :param standard_offset_from_utc: Time zone with respect to Greenwich Mean Time (GMT) in +/- hours offset.
        :type standard_offset_from_utc: float

        :return: A dictionary containing the project id.
        :rtype: dict
        """

        self.name = name if name is not None else self.name
        self.latitude = latitude if latitude is not None else self.latitude
        self.longitude = longitude if longitude is not None else self.longitude
        self.country = country if country is not None else self.country
        self.country_code = country_code if country_code is not None else self.country_code
        self.elevation = elevation if elevation is not None else self.elevation
        self.standard_offset_from_utc = standard_offset_from_utc if standard_offset_from_utc is not None \
            else self.standard_offset_from_utc

        self.create_url_suffix = "/Project"

        return super(Project, self).create()

    def delete(self):
        """HTTP Request: DELETE /Project/{ProjectId}

        Deletes an existing Project entity in PlantPredict. The local instance of the Project entity must have
        attribute self.id identical to the project id of the Project to be deleted.

        :return: A dictionary {"is_successful": True}.
        :rtype: dict
        """

        self.delete_url_suffix = "/Project/{}".format(self.id)

        return super(Project, self).delete()

    def get(self):
        """HTTP Request: GET /Project/{Id}

        Retrieves an existing Project entity in PlantPredict and automatically assigns all of its attributes to the
        local Project object instance. The local instance of the Project entity must have attribute self.id identical
        to the project id of the Project to be retrieved.

        :return: A dictionary containing all of the retrieved Project attributes.
        :rtype: dict
        """

        self.get_url_suffix = "/Project/{}".format(self.id)

        return super(Project, self).get()

    def update(self):
        """HTTP Request: PUT /Project

        Updates an existing Project entity in PlantPredict using the full attributes of the local Project instance.
        Calling this method is most commonly preceded by instantiating a local instance of Project with a specified
        project id, calling the Project.get() method, and changing any attributes locally.

        :return: A dictionary {"is_successful": True}.
        :rtype: dict
        """
        self.update_url_suffix = "/Project"

        return super(Project, self).update()

    @handle_refused_connection
    @handle_error_response
    def get_all_predictions(self):
        """HTTP Request: GET /Project/{ProjectId}/Prediction

        Retrieves the full attributes of every Prediction associated with the Project.

        :return: A list of dictionaries, each containing the attributes of a Prediction entity.
        :rtype: list of dict
        """

        return requests.get(
            url=settings.BASE_URL + "/Project/{}/Prediction".format(self.id),
            headers={"Authorization": "Bearer " + settings.TOKEN}
        )

    @staticmethod
    def search(latitude, longitude, search_radius=1.0):
        """HTTP Request: GET /Project/Search

        Searches for all existing Project entities within a search radius of a specified latitude/longitude.

        :param latitude: North-South coordinate of the Project location, in decimal degrees.
        :type latitude: float
        :param longitude: East-West coordinate of the Project location, in decimal degrees.
        :type longitude: float
        :param search_radius: search radius in miles
        :type search_radius: float
        :return: int, float
        """
        response = requests.get(
            url=settings.BASE_URL + "/Project/Search",
            headers={"Authorization": "Bearer " + settings.TOKEN},
            params={'latitude': latitude, 'longitude': longitude, 'searchRadius': search_radius}
        )

        project_list = json.loads(response.content)

        return [convert_json(p, camel_to_snake) for p in project_list]

    def __init__(self, id=None):
        if id:
            self.id = id

        self.name = None
        self.latitude = None
        self.longitude = None
        self.country = None
        self.country_code = None
        self.elevation = None
        self.standard_offset_from_utc = None

        super(Project, self).__init__()
