import requests
from plantpredict import settings
from plantpredict.plant_predict_entity import PlantPredictEntity
from plantpredict.powerplant import PowerPlant
from plantpredict.user import User
from plantpredict.utilities import convert_json, snake_to_camel
from plantpredict.error_handlers import handle_refused_connection, handle_error_response
from plantpredict.enumerations.prediction_status_enum import *


class Prediction(PlantPredictEntity):
    """
    The full contents of the Prediction database entity (in JSON) can be found under
    "GET /Project/{ProjectId}/Prediction/{PredictionId}" in `the general PlantPredict API documentation
    <http://app.plantpredict.com/swagger/ui/index#!/Project/Project_GetPrediction>`_.
    """

    def create(self, name=None, project_id=None, status=DRAFT_PRIVATE, year_repeater=1):
        """HTTP Request: POST /Project/{ProjectId}/Prediction

        Creates a new Prediction entity in PlantPredict and assigns the uid of the newly created Prediction to self.id
        in the local object instance. Any attributes (including but not limited to those also assignable via the inputs
        to this method) assigned prior to calling this method will be recorded in the new Prediction entity in
        PlantPredict. The input variables to this method are those required for successful Prediction creation.

        :param name: The name of the Prediction.
        :type name: str
        :param project_id: Unique identifier of the Project (parent) with which the Prediction (child) should be associated.
        :type project_id: int
        :param status: The Prediction's status enumeration (defaulted to DRAFT-PRIVATE), defined and imported in plantpredict.enumerations.prediction_status_enum.
        :type status: int
        :param year_repeater: Number of years of power plant operation to be simulated (defaulted to 1 year).
        :type year_repeater: int

        :return: A dictionary containing the prediction id.
        :rtype: dict
        """
        self.name = name if name is not None else self.name
        self.project_id = project_id if project_id is not None else self.project_id
        self.status = status if self.status is None else self.status
        self.year_repeater = year_repeater if self.year_repeater is None else self.year_repeater

        self.create_url_suffix = "/Project/{}/Prediction".format(self.project_id)

        return super(Prediction, self).create()

    def delete(self):
        """HTTP Request: DELETE /Project/{ProjectId}/Prediction/{Id}

        Deletes an existing Prediction entity in PlantPredict. The local instance of the Project entity must have
        attribute self.id identical to the prediction id of the Prediction to be deleted.

        :return: A dictionary {"is_successful": True}.
        :rtype: dict
        """
        self.delete_url_suffix = "/Project/{}/Prediction/{}".format(self.project_id, self.id)

        return super(Prediction, self).delete()

    def get(self, id=None, project_id=None):
        """HTTP Request: GET /Project/{ProjectId}/Prediction/{Id}

        Retrieves an existing Prediction entity in PlantPredict and automatically assigns all of its attributes to the
        local Prediction object instance. The local instance of the Prediction entity must have attribute self.id
        identical to the prediction id of the Prediction to be retrieved.

        :return: A dictionary containing all of the retrieved Prediction attributes.
        :rtype: dict

        """
        self.id = id if id is not None else self.id
        self.project_id = project_id if project_id is not None else self.project_id

        self.get_url_suffix = "/Project/{}/Prediction/{}".format(self.project_id, self.id)

        return super(Prediction, self).get()

    def update(self):
        """HTTP Request: PUT /Project/{ProjectId}/Prediction

        Updates an existing Prediction entity in PlantPredict using the full attributes of the local Prediction
        instance. Calling this method is most commonly preceded by instantiating a local instance of Prediction with a
        specified prediction id, calling the Prediction.get() method, and changing any attributes locally.

        :return: A dictionary {"is_successful": True}.
        :rtype: dict
        """

        self.update_url_suffix = "/Project/{}/Prediction".format(self.project_id)

        return super(Prediction, self).update()

    @handle_refused_connection
    def _wait_for_prediction(self):
        is_complete = False
        while not is_complete:
            task_queue = User.get_queue()
            try:
                prediction_task = (task for task in task_queue if task['predictionId'] == self.id).next()
            except (StopIteration, TypeError):
                continue

            # Processing Status Enum (Success = 3)
            # TODO 4 is error but works for module file stuff
            if prediction_task['prediction']['processingStatus'] in [3, 4]:
                is_complete = True

    @handle_refused_connection
    @handle_error_response
    def run(self, export_options=None):
        """
        POST /Project/{ProjectId}/Prediction/{PredictionId}/Run

        Runs the Prediction and waits for simulation to complete. The input variable "export_options" should take the

        :param export_options: Contains options for exporting
        :return:
        """

        response = requests.post(
            url=settings.BASE_URL + "/Project/{}/Prediction/{}/Run".format(self.project_id, self.id),
            headers={"Authorization": "Bearer " + settings.TOKEN},
            json=convert_json(export_options, snake_to_camel) if export_options else None
        )

        # observes task queue to wait for prediction run to complete
        self._wait_for_prediction()

        return response

    @handle_refused_connection
    @handle_error_response
    def get_results_summary(self):
        """GET /Project/{ProjectId}/Prediction/{Id}/ResultSummary"""

        return requests.get(
            url=settings.BASE_URL + "/Project/{}/Prediction/{}/ResultSummary".format(self.project_id, self.id),
            headers={"Authorization": "Bearer " + settings.TOKEN}
        )

    @handle_refused_connection
    @handle_error_response
    def get_results_details(self):
        """GET /Project/{ProjectId}/Prediction/{Id}/ResultDetails"""

        return requests.get(
            url=settings.BASE_URL + "/Project/{}/Prediction/{}/ResultDetails".format(self.project_id, self.id),
            headers={"Authorization": "Bearer " + settings.TOKEN}
        )

    @handle_refused_connection
    @handle_error_response
    def get_nodal_data(self, params):
        """GET /Project/{ProjectId}/Prediction/{Id}/NodalJson"""

        return requests.get(
            url=settings.BASE_URL + "/Project/{}/Prediction/{}/NodalJson".format(self.project_id, self.id),
            headers={"Authorization": "Bearer " + settings.TOKEN},
            params=convert_json(params, snake_to_camel)
        )

    @handle_refused_connection
    @handle_error_response
    def clone(self, new_prediction_name):
        """

        Parameters
        ----------
        new_prediction_name

        Returns
        -------

        """
        # clone prediction
        new_prediction = Prediction()
        self.get()
        original_prediction_id = self.id

        new_prediction.__dict__ = self.__dict__
        # initialize necessary fields
        new_prediction.__dict__.pop('prediction_id', None)
        new_prediction.__dict__.pop('created_date', None)
        new_prediction.__dict__.pop('last_modified', None)
        new_prediction.__dict__.pop('last_modified_by', None)
        new_prediction.__dict__.pop('last_modified_by_id', None)
        new_prediction.__dict__.pop('project', None)
        new_prediction.__dict__.pop('power_plant_id', None)
        new_prediction.__dict__.pop('powerplant', None)

        new_prediction.name = new_prediction_name
        new_prediction.create()
        new_prediction_id = new_prediction.id

        # clone powerplant and attach to new prediction
        new_powerplant = PowerPlant()
        powerplant = PowerPlant(project_id=self.project_id, prediction_id=original_prediction_id)
        powerplant.get()
        new_powerplant.__dict__ = powerplant.__dict__
        new_powerplant.prediction_id = new_prediction_id
        new_powerplant.__dict__.pop('id', None)

        # initialize necessary fields
        for block in new_powerplant.blocks:
            block.pop('id', None)
            for array in block['arrays']:
                array.pop('id', None)
                for inverter in array['inverters']:
                    inverter.pop('id', None)
                    for dc_field in inverter['dc_fields']:
                        dc_field.pop('id', None)

        new_powerplant.create()

        self.id = original_prediction_id
        self.get()

        return new_prediction_id

    def __init__(self, id=None, project_id=None):
        if id:
            self.id = id
        self.project_id = project_id

        self.name = None
        self.status = None
        self.year_repeater = None

        super(Prediction, self).__init__()
