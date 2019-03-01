import requests
from plantpredict import settings
from plantpredict.plant_predict_entity import PlantPredictEntity
from plantpredict.powerplant import PowerPlant
from plantpredict.utilities import convert_json, snake_to_camel
from plantpredict.error_handlers import handle_refused_connection, handle_error_response


class Prediction(PlantPredictEntity):
    """
    The :py:mod:`plantpredict.Prediction` entity models a single energy prediction within a
    :py:mod:`plantpredict.Project`.
    """
    def create(self):
        """
        **POST** */Project/ :py:attr:`project_id` /Prediction*

        Creates a new :py:mod:`plantpredict.Prediction` entity in the PlantPredict database using the attributes
        assigned to the local object instance. Automatically assigns the resulting :py:attr:`id` to the local object
        instance. See the minimum required attributes (below) necessary to successfully create a new
        :py:mod:`plantpredict.Prediction`. Note that the full scope of attributes is not limited to the minimum
        required set. **Important Note:** the minimum required attributes necessary to create a
        :py:mod:`plantpredict.Prediction` is not sufficient to successfully call :py:meth:`plantpredict.Prediction.run`.

        .. container:: toggle

            .. container:: header

                **Required Attributes**

            .. container:: required_attributes

                .. csv-table:: Minimum required attributes for successful Prediction creation
                    :delim: ;
                    :header: Field, Type, Description
                    :stub-columns: 1

                    name; str; Name of prediction
                    project_id; int; ID of project within which to contain the prediction
                    status; int; Represents the Prediction status (Draft-Private, Draft-Shared, Analysis, etc). Use :py:mod:`plantpredict.enumerations.prediction_status_enum`.
                    year_repeater; int; Must be between :py:data:`1` and :py:data:`50` - unitless.

        .. container:: toggle

            .. container:: header

                **Example Code**

            .. container:: example_code

                First, import the plantpredict library and receive an authentication plantpredict.settings.TOKEN in your
                Python session, as shown in Step 3 of :ref:`authentication_oauth2`. Then instantiate a local Prediction.
                object.

                .. code-block:: python

                    module_to_create = plantpredict.Prediction()

                Populate the Prediction's require attributes by either directly assigning them...

                .. code-block:: python

                    from plantpredict.enumerations import prediction_status_enum

                    prediction_to_create.name = "Test Prediction"
                    prediction_to_create.project_id = 1000
                    prediction_to_create.status = prediction_status_enum.DRAFT_SHARED
                    prediction_to_create.year_repeater = 1

                ...OR via dictionary assignment.

                .. code-block:: python

                    prediction_to_create.__dict__ = {
                        "name": "Test Prediction",
                        "model": "Test Module",
                        "status": prediction_status_enum.DRAFT_SHARED,
                        "year_repeater": 1,
                    }

                Create a new prediction in the PlantPredict database, and observe that the Module now has a unique
                database identifier.

                .. code-block:: python

                    prediction_to_create.create()

                    print prediction_to_create.id

        :return: A dictionary containing the prediction id.
        :rtype: dict
        """

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
            self.get()
            if self.processing_status == 3:
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
