.. _example_usage:

Example Usage
=============

The code snippets below are practical examples of useful tasks accomplished via PlantPredict's API. All of the code
used in the examples below is available via `the source code on Github
<https://github.com/stephenkaplan/plantpredict-python/tree/master/example_usage>`_. Feel free to use and modify the
code in your local environment.

Every example assumes that you first :code:`import plantpredict` and authenticate with
:py:class:`~plantpredict.api.Api` as shown in Step 3 of :ref:`authentication_oauth2`.

Create Project and Prediction from scratch.
-------------------------------------------

This is one example of how to build a project, prediction, and attach a power plant. There are a variety of optional
settings for every component that can't be captured in a single example. Please refer to the documentation for
:py:class:`~plantpredict.project.Project`, :py:class:`~plantpredict.prediction.Prediction`, and
:py:class:`~plantpredict.powerplant.PowerPlant` for more information.

Instantiate a local instance of :py:class:`~plantpredict.project.Project`, assigning :py:attr:`name`,
:py:attr:`latitude`, and :py:attr:`longitude`.

.. code-block:: python

    project = api.project(name="Area 51 Alien Power Plant", latitude=37.23, longitude=-115.80)

Assign location attributes with helper method :py:meth:`~plantpredict.project.Project.assign_location_attributes`, and
create as the local instance of :py:class:`~plantpredict.project.Project` a new entity in the PlantPredict database.

.. code-block:: python

    project.assign_location_attributes()
    project.create()

Instantiate a local instance of :py:class:`~plantpredict.prediction.Prediction`, assigning :py:attr:`project_id` (from
the newly created project) and :py:attr:`name`.

.. code-block:: python

    prediction = api.prediction(project_id=project.id, name="Area 51 - Contracted")

Assign the :py:attr:`weather_id` corresponding to the weather file you want to use (assuming it already exists in the
PlantPredict database).

.. code-block:: python

    prediction.weather_id = 13628

Instantiate and retrieve the weather file, and ensure that the two pairs of prediction start/end attributes match those
of the weather file.

.. code-block:: python

    weather = api.weather(id=prediction.weather_id)
    weather.get()
    prediction.start_date = weather.start_date
    prediction.end_date = weather.end_date
    prediction.start = weather.start_date
    prediction.end = weather.end_date

Import all of the enumeration files relevant to prediction settings. Set ALL of the following model options on the
prediction using the enumerations library in :py:mod:`~plantpredict.enumerations` similar to the code below, but to
your preferences.

.. code-block:: python

    from plantpredict.enumerations import PredictionStatusEnum, TranspositionModelEnum, SpectralShiftModelEnum, \
        DiffuseDirectDecompositionModelEnum, ModuleTemperatureModelEnum, IncidenceAngleModelTypeEnum, \
        AirMassModelTypeEnum, DirectBeamShadingModelEnum, SoilingModelTypeEnum, DegradationModelEnum, \
        TrackingTypeEnum, BacktrackingTypeEnum, DiffuseShadingModelEnum

    prediction.diffuse_direct_decomp_model = DiffuseDirectDecompositionModelEnum.NONE
    prediction.transposition_model = TranspositionModelEnum.PEREZ
    prediction.mod_temp_model = ModuleTemperatureModelEnum.HEAT_BALANCE
    prediction.inc_angle_model = IncidenceAngleModelTypeEnum.TABULAR_IAM
    prediction.spectral_shift_model = SpectralShiftModelEnum.TWO_PARAM_PWAT_AND_AM
    prediction.air_mass_model = AirMassModelTypeEnum.BIRD_HULSTROM
    prediction.direct_beam_shading_model = DirectBeamShadingModelEnum.LINEAR
    prediction.diffuse_shading_model = DiffuseShadingModelEnum.SCHAAR_PANCHULA
    prediction.soiling_model = SoilingModelTypeEnum.CONSTANT_MONTHLY
    prediction.monthly_factors = [
        {"month": 1, "month_name": "Jan", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 2, "month_name": "Feb", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 3, "month_name": "Mar", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 4, "month_name": "Apr", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 5, "month_name": "May", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 6, "month_name": "Jun", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 7, "month_name": "Jul", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 8, "month_name": "Aug", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 9, "month_name": "Sep", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 10, "month_name": "Oct", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 11, "month_name": "Nov", "albedo": 0.2, "soiling_loss": 2.0},
        {"month": 12, "month_name": "Dec", "albedo": 0.2, "soiling_loss": 2.0},
    ]
    prediction.diffuse_direct_decomp_model_executed = True
    prediction.use_meteo_dni = False
    prediction.use_meteo_poai = False
    prediction.degradation_model = DegradationModelEnum.LINEAR_DC
    prediction.linear_degradation_rate = 0.5
    prediction.first_year_degradation = False
    prediction.year_repeater = 3

Create the prediction in the PlantPredict database.

.. code-block:: python

    prediction.create()

Change the prediction's status to :py:attr:`plantpredict.enumerations.PredictionStatusEnum.DRAFT-SHARED` to make it
accessible to other members of your team (or to another relevant status).

.. code-block:: python

    prediction.change_status(new_status=PredictionStatusEnum.DRAFT_SHARED, note="Changed for tutorial.")

Instantiate a local instance of :py:class:`~plantpredict.powerplant.PowerPlant`, assigning its :py:attr:`project_id` and
:py:attr:`prediction_id`.

.. code-block:: python

    powerplant = api.powerplant(project_id=project.id, prediction_id=prediction.id)

Add a fixed tilt block, array, inverter, and dc field using :py:meth:`~plantpredict.powerplant.PowerPlant.add_block`,
:py:meth:`~plantpredict.powerplant.PowerPlant.add_array`, :py:meth:`~plantpredict.powerplant.PowerPlant.add_inverter`
and :py:meth:`~plantpredict.powerplant.PowerPlant.add_dc_field`, respectively. In this example, not all optional fields
are used in this method. Refer to each method's documentation for information on what other
power plant attributes can be configured. Additionally, refer to the `PlantPredict User Guide
<https://plantpredict.com/user_manual/predictions/#power-plant-builder>`_ for documentation on power plant
hierarchy.

.. code-block:: python

    fixed_tilt_block_name = powerplant.add_block()
    fixed_tilt_array_name = powerplant.add_array(
        block_name=fixed_tilt_block_name,
        transformer_enabled=False,
        repeater=3,
        description="Arrays in north eastern section of plant."
    )
    fixed_tilt_inverter_name = powerplant.add_inverter(
        block_name=fixed_tilt_block_name,
        array_name=fixed_tilt_array_name,
        inverter_id=619,
        setpoint_kw=720.0,
        repeater=2
    )

Assuming there is one DC field on the inverter, the field DC power can be calculated from a DC AC ratio. If there
were two identical DC fields on a single inverter, you would use half of the number of strings. For irregular
configurations, perform a custom calculation for number of strings in parallel and field dc power. Additionally, the
post to post spacing can be calculated from GCR and some information about the module being used in the DC field. Use
the helpers to prepare field DC power and post to post spacing, and then add the fixed tilt DC field.

.. code-block:: python

    field_dc_power = powerplant.calculate_field_dc_power_from_dc_ac_ratio(dc_ac_ratio=1.2, inverter_setpoint=720.0)
    post_to_post_spacing = powerplant.calculate_post_to_post_spacing_from_gcr(ground_coverage_ratio=0.40, module_id=298,
                                                                              modules_high=4)

    fixed_tilt_dc_field_name = powerplant.add_dc_field(
        block_name=fixed_tilt_block_name,
        array_name=fixed_tilt_array_name,
        inverter_name=fixed_tilt_inverter_name,
        module_id=298,
        tracking_type=TrackingTypeEnum.FIXED_TILT,
        modules_high=4,
        modules_wired_in_series=10,
        post_to_post_spacing=post_to_post_spacing,
        number_of_rows=10,
        field_dc_power=field_dc_power,
        module_tilt=30
    )

You can continue to add new blocks, or even add arrays to blocks, inverters to arrays, etc. The code below is an
example of adding a block with a DC field that uses single-axis tracking.

.. code-block:: python

    tracker_block_name = powerplant.add_block()
    tracker_array_name = powerplant.add_array(
        block_name=tracker_block_name,
        transformer_enabled=False,
    )
    tracker_inverter_name = powerplant.add_inverter(
        block_name=tracker_block_name,
        array_name=tracker_array_name,
        inverter_id=619,
        setpoint_kw=720.0
    )

Prepare the field DC power and post to post spacing for the tracker DC field, and then add it to the inverter.

.. code-block:: python

    field_dc_power = powerplant.calculate_field_dc_power_from_dc_ac_ratio(dc_ac_ratio=1.1, inverter_setpoint=720.0)
    post_to_post_spacing = powerplant.calculate_post_to_post_spacing_from_gcr(ground_coverage_ratio=0.20, module_id=298,
                                                                              modules_high=1)

    tracker_dc_field_name = powerplant.add_dc_field(
        block_name=tracker_block_name,
        array_name=tracker_array_name,
        inverter_name=tracker_inverter_name,
        module_id=298,
        tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
        modules_high=1,
        modules_wired_in_series=10,
        post_to_post_spacing=post_to_post_spacing,
        number_of_rows=10,
        field_dc_power=field_dc_power,
        tracking_backtracking_type=BacktrackingTypeEnum.TRUE_TRACKING
    )

Create the local instance of :py:class:`~plantpredict.powerplant.PowerPlant` as a new entity in the PlantPredict
database. Since the id's of the project and prediction created previously were assigned to the PowerPlant, it will
automatically attach to the prediction in PlantPredict.

.. code-block:: python

    powerplant.create()

The prediction can now be run.

.. code-block:: python

    prediction.run()

Model System-Level of Power Plant (Transformer, Transmission, etc.)
---------------------------------------------------------------------

This tutorial details how to model Total System Capacity, Transformers and Transmission Lines for a power plant/energy
prediction. This can be done upon initial creation of a prediction from scratch (see the example for
`Create Project and Prediction from scratch.`_), but for the sake of example, we will consider the case of updating an
existing power plant.

Instantiate a :py:class:`~plantpredict.powerplant.PowerPlant`, specifying its :py:attr:`project_id` and
:py:attr:`prediction_id` (visible in the URL of that prediction in a web browser
... :py:data:`/projects/{project_id}/prediction/{id}`).

.. code-block:: python

    project_id = 13161   # CHANGE TO YOUR PROJECT ID
    prediction_id = 147813   # CHANGE TO YOUR PREDICTION ID
    powerplant = api.powerplant(project_id=project_id, prediction_id=prediction_id)

Retrieve the power plant's attributes.

.. code-block:: python

    powerplant.get()

Set the system :py:attr:`availability_loss` on the :py:class:`~plantpredict.powerplant.PowerPlant` instance in units
:py:data:`[%]`.

.. code-block:: python

    powerplant.availability_loss = 1.7

Set the plant output (LGIA) limit in units :py:data:`[MWac]`.

.. code-block:: python

    powerplant.lgia_limitation = 0.8

Add :py:attr:`transformers` and :py:data:`transmission_lines`, specifying the :py:attr:`ordinal` (1-indexed) such that
they are in the desired order (where 1 is closest to the physical output of the plant).

.. code-block:: python

    powerplant.add_transformer(rating=0.6, high_side_voltage=600, no_load_loss=1.1, full_load_loss=1.7, ordinal=1)
    powerplant.add_transmission_line(length=3, resistance=0.1, number_of_conductors_per_phase=1, ordinal=2)

Call the :py:meth:`~plantpredict.powerplant.PowerPlant.update` method on the instance of
:py:class:`~plantpredict.powerplant.PowerPlant` to persist these changes to PlantPredict.

.. code-block:: python

    powerplant.update()

Download nodal data.
---------------------

First, set up a dictionary containing the nodal data export options. Set the values to True according to which nodes
in the :py:class:`~plantpredict.powerplant.PowerPlant` hierarchy you are interested in exporting nodal data. For each
block in :py:data:`block_export_options`, specify the block number (using the field :py:data:`name`).
You can add export options for multiple blocks, but in this example we just do one.

.. code-block:: python

    export_options = {
        'export_system': True,
        'block_export_options': [{
            "name": 1,
            "export_block": False,
            "export_arrays": True,
            "export_inverters": False,
            "export_dc_fields": True
        }]
    }

Instantiate a new prediction using the :py:class:`~plantpredict.prediction.Prediction` class, specifying its
:py:attr:`id` and :py:attr:`project_id` (visible in the URL of that prediction in a web browser
... :py:data:`/projects/{project_id}/prediction/{id}/`).

.. code-block:: python

    project_id = 13161   # CHANGE TO YOUR PROJECT ID
    prediction_id = 147813   # CHANGE TO YOUR PREDICTION ID
    prediction = api.prediction(id=prediction_id, project_id=project_id)

Run the prediction.

.. code-block:: python

    prediction.run(export_options=export_options)

Retrieve the nodal data of Array 1 (in Block 1) and DC  Field 1 (in Block 1 --> Array 1 --> Inverter A). Note that
the lowest node (power plant hierarchy-wise) in the input dictionary specifies the nodal data returned.

.. code-block:: python

    nodal_data_array = prediction.get_nodal_data(params={
        'block_number': 1,
        'array_number': 1,
    })

    nodal_data_dc_field = prediction.get_nodal_data(params = {
        'block_number': 1,
        'array_number': 1,
        'inverter_name': 'A',
        'dc_field_number': 1
    })

For system-level nodal data, call the method with no inputs.

.. code-block:: python

    nodal_data_system = prediction.get_nodal_data()

The nodal data returned will be returned as JSON serializable data, as detailed in the documentation for
:py:func:`~plantpredict.prediction.Prediction.get_nodal_data`.


Clone a prediction.
-------------------

Instantiate the prediction you wish to clone using the :py:class:`~plantpredict.prediction.Prediction` class, specifying
its :py:attr:`id` and :py:attr:`project_id` (visible in the URL of that prediction in a web browser
... :py:data:`/projects/{project_id}/prediction/{id}/`).

.. code-block:: python

    project_id = 13161   # CHANGE TO YOUR PROJECT ID
    prediction_id = 147813   # CHANGE TO YOUR PREDICTION ID
    prediction_to_clone = api.prediction(id=prediction_id, project_id=project_id)


Clone the prediction, passing in a name for the new prediction. This will create a new prediction within the same
project that is an exact copy (other than the name) of the original prediction.

.. code-block:: python

    new_prediction_id = prediction_to_clone.clone(new_prediction_name='Cloned Prediction')

If you wish to change something about the new prediction, instantiate a new
:py:class:`~plantpredict.prediction.Prediction` with the returned prediction ID, change an attribute, and call the
:py:meth:`~plantpredict.prediction.Prediction.update` method.

.. code-block:: python

    new_prediction = api.prediction(id=new_prediction_id, project_id=project_id)
    new_prediction.get()
    from plantpredict.enumerations import TranspositionModelEnum    # import at the top of the file
    new_prediction.transposition_model = TranspositionModelEnum.HAY
    new_prediction.update()


Change the module in a power plant.
-----------------------------------

Instantiate the powerplant of the prediction of interest using the
:py:class:`~plantpredict.powerplant.PowerPlant` class, specifying the :py:attr:`project_id` and :py:attr:`prediction_id`
(visible in the URL of that prediction in a web browser ... :py:data:`/projects/{project_id}/prediction/{id}/`).

.. code-block:: python

    project_id = 13161   # CHANGE TO YOUR PROJECT ID
    prediction_id = 147813   # CHANGE TO YOUR PREDICTION ID
    powerplant = api.powerplant(prediction_id=prediction_id, project_id=project_id)

Retrieve all of its attributes.

.. code-block:: python

    powerplant.get()

Specify the :py:attr:`id` of the module you want to replace the power plant's current module with (visible in the URL
of that module in a web browser ... :py:data:`/module/{id}/`). Retrieve the module.

.. code-block:: python

    new_module_id = 3047
    new_module = api.module(id=new_module_id)
    new_module.get()

In order to change the module in Block 1 --> Array 1 --> Inverter A --> DC Field 1,
replace the previous module's data structure, replace the module id, and update the power plant with the
the :py:func:`~plantpredict.powerplant.PowerPlant.update` method.

.. code-block:: python

    powerplant.blocks[0]['arrays'][0]['inverters'][0]['dc_fields'][0]['module'] = new_module.__dict__
    powerplant.blocks[0]['arrays'][0]['inverters'][0]['dc_fields'][0]['module_id'] = new_module_id
    powerplant.update()


Change a prediction's weather file.
------------------------------------

Instantiate the prediction of interest using the :py:class:`~plantpredict.prediction.Prediction` class, specifying its
:py:attr:`id` and :py:attr:`project_id` (visible in the URL of that prediction in a web browser
... :py:data:`/projects/{project_id}/prediction/{id}/`). Do the same for the project of interest using the
:py:class:`~plantpredict.project.Project` class.

.. code-block:: python

    project_id = 13161   # CHANGE TO YOUR PROJECT ID
    prediction_id = 147813   # CHANGE TO YOUR PREDICTION ID
    prediction = api.prediction(id=prediction_id, project_id=project_id)
    project = api.project(id=project_id)

Retrieve the project and prediction's attributes.

.. code-block:: python

    prediction.get()
    project.get()

In this particular case, let's say you are looking for the most recent Meteonorm weather file within a 5-mile
radius of the project site. Search for all weather files within a 5 mile radius of the project's
:py:attr:`latitude`/:py:attr:`longitude` coordinates.

.. code-block:: python

    w = api.weather()
    weathers = w.search(project.latitude, project.longitude, search_radius=5)

Filter the results by only Meteonorm weather files.

.. code-block:: python

    from plantpredict.enumerations import WeatherDataProviderEnum  # should import at the top of your file
    weathers_meteo = [weather for weather in weathers if int(weather['data_provider']) == WeatherDataProviderEnum.METEONORM]

If there is a weather file that meets the criteria, used the most recently created weather file's :py:attr:`id`. If no
weather file meets the criteria, download a new Meteonorm (or whatever type you are working with) weather file and use
that :py:attr:`id`.

.. code-block:: python

    from plantpredict.enumerations import WeatherSourceTypeAPIEnum
    if weathers_meteo:
        created_dates = [w['created_date'] for w in weathers_meteo]
        created_dates.sort()
        idx = [w['created_date'] for w in weathers_meteo].index(created_dates[-1])
        weather_id = weathers_meteo[idx]['id']
    else:
        weather = api.weather()
        response = weather.download(project.latitude, project.longitude, provider=WeatherSourceTypeAPIEnum.METEONORM)
        weather_id = weather.id

Instantiate weather using the weather :py:attr:`id` and retrieve all of its attributes.

.. code-block:: python

    weather = api.weather(id=weather_id)
    weather.get()

Ensure that the prediction :py:attr:`start`/:py:attr:`end` attributes match those of the weather file.

.. code-block:: python

    prediction.start_date = weather.start_date
    prediction.end_date = weather.end_date
    prediction.start = weather.start_date
    prediction.end = weather.end_date

Change the :py:attr:`weather_id` of the prediction and update the prediction.

.. code-block:: python

    prediction.weather_id = weather_id
    prediction.update()

Upload raw weather data.
-------------------------

Whether you are starting with an Excel file, CSV file, SQL query, or other data format, the first step is to get your
data into a JSON-like format. That format is represented in Python as a list of dictionaries, where each dictionary
represents a timestamp of weather data. Depending on the initial data format, you can utilize any of Python's
open-source data tools such as the `native csv library
<https://docs.python.org/2/library/csv.html>`_ or
`pandas <https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_excel.html>`_. This tutorial skips that step
and loads pre-processed data from :download:`this JSON file <_static/weather_details.json>`.

.. code-block:: python

    import json
    with open('weather_details.json', 'rb') as json_file:
        weather_details = json.load(json_file)

Using the known latitude and longitude of the weather data location, call
:py:meth:`~plantpredict.geo.Geo.get_location_info` query crucial location info necessary to populate the weather file's
metadata.

.. code-block:: python

    latitude = 35.0
    longitude = -119.0
    geo = api.geo(latitude=latitude, longitude=longitude)
    location_info = geo.get_location_info()

Initialize the :py:class:`~plantpredict.weather.Weather` entity and populate with the minimum fields required by
:py:meth:`~plantpredict.weather.Weather.create`. Note that the weather details time series data loaded in the first step
is assigned to :py:attr:`weather_details` at this point.

.. code-block:: python

    from plantpredict.enumerations import WeatherDataProviderEnum
    weather = api.weather()
    weather.name = "Python SDK Test Weather"
    weather.latitude = 35.0
    weather.longitude = -119.0
    weather.country = location_info['country']
    weather.country_code = location_info['country_code']
    weather.data_provider = WeatherDataProviderEnum.METEONORM
    weather.weather_details = weather_details

Assign additional metadata fields.

.. code-block:: python

    weather.elevation = round(geo.get_elevation()["elevation"], 2)
    weather.locality = location_info['locality']
    weather.region = location_info['region']
    weather.state_province = location_info['state_province']
    weather.state_province_code = location_info['state_province_code']
    weather.time_zone = geo.get_time_zone()['time_zone']
    weather.status = LibraryStatusEnum.DRAFT_PRIVATE
    weather.data_type = WeatherDataTypeEnum.MEASURED
    weather.p_level = WeatherPLevelEnum.P95
    weather.time_interval = 60  # minutes
    weather.global_horizontal_irradiance_sum = round(
        sum([w['global_horizontal_irradiance'] for w in weather_details])/1000, 2
    )
    weather.diffuse_horizontal_irradiance_sum = round(
        sum([w['diffuse_horizontal_irradiance'] for w in weather_details])/1000, 2
    )
    weather.direct_normal_irradiance_sum = round(
        sum([w['direct_normal_irradiance'] for w in weather_details])/1000, 2
    )
    weather.average_air_temperature = np.round(np.mean([w['temperature'] for w in weather_details]), 2)
    weather.average_relative_humidity = np.round(np.mean([w['relative_humidity'] for w in weather_details]), 2)
    weather.average_wind_speed = np.round(np.mean([w['windspeed'] for w in weather_details]), 2)
    weather.max_air_temperature = np.round(max([w['temperature'] for w in weather_details]), 2)

Create the weather file in PlantPredict with :py:meth:`~plantpredict.weather.Weather.create`.

.. code-block:: python

    weather.create()


Generate a module file.
------------------------

Instantiate a :py:mod:`~plantpredict.module.Module` object.

.. code-block:: python

    module = api.module()

Assign basic module parameters from the manufacturer's datasheet or similar data source.

.. code-block:: python

    from plantpredict.enumerations import CellTechnologyTypeEnum, PVModelTypeEnum
    module.cell_technology_type = CellTechnologyTypeEnum.CDTE
    module.number_of_cells_in_series = 264
    module.pv_model = PVModelTypeEnum.ONE_DIODE_RECOMBINATION
    module.reference_temperature = 25
    module.reference_irradiance = 1000
    module.stc_max_power = 430.0
    module.stc_short_circuit_current = 2.54
    module.stc_open_circuit_voltage = 219.2
    module.stc_mpp_current = 2.355
    module.stc_mpp_voltage = 182.55
    module.stc_power_temp_coef = -0.32
    module.stc_short_circuit_current_temp_coef = 0.04
    module.stc_open_circuit_voltage_temp_coef = -0.28

Generate single diode parameters using the
`default algorithm/assumptions <https://plantpredict.com/algorithm/module-file-generator/>`_.

.. code-block:: python

    module.generate_single_diode_parameters_default()

At this point, the user could simply add the remaining required fields and save the new module. Alternatively, the
user can tune the module's single diode parameters to achieve (close to) a desired effective irradiance
response (EIR)/low-light performance. The first step is to define target relative efficiencies at specified
irradiance.

.. code-block:: python

    module.effective_irradiance_response = [
        {'temperature': 25, 'irradiance': 1000, 'relative_efficiency': 1.0},
        {'temperature': 25, 'irradiance': 800, 'relative_efficiency': 1.0029},
        {'temperature': 25, 'irradiance': 600, 'relative_efficiency': 1.0003},
        {'temperature': 25, 'irradiance': 400, 'relative_efficiency': 0.9872},
        {'temperature': 25, 'irradiance': 200, 'relative_efficiency': 0.944}
    ]

How a user chooses to tune the module's performance is relatively open-ended, but a good place to start is using
PlantPredict's `Optimize Series Resistance" algorithm <https://plantpredict.com/algorithm/module-file-generator/#optimize-series-resistance-to-match-eir-algorithm>`_.
This will automatically change the series resistance to generate an EIR closer to the target, and re-calculate all
single-diode parameters dependent on series resistance.

.. code-block:: python

    module.optimize_series_resistance()

At any point the user can check the current model-calculated EIR to compare it to the target.

.. code-block:: python

    calculated_effective_irradiance_response = module.calculate_effective_irradiance_response()

An IV curve can be generated for the module for reference.

.. code-block:: python

    iv_curve_at_stc = module.generate_iv_curve(num_iv_points=250)

The initial series resistance optimization might not achieve an EIR close enough to the target. the user can modify
any parameter, re-optimize series resistance or just recalculate dependent parameters, and check EIR repeatedly.
This is the open-ended portion of module file generation. Important Note: after modifying parameters, if the user
does not re-optimize series resistance, :py:meth:`~plantpredict.module.Module.generate_single_diode_parameters_advanced`
must be called to re-calculate :py:attr:`saturation_current_at_stc`, :py:attr:`diode_ideality_factor_at_stc`,
:py:attr:`light_generated_current`, :py:attr:`linear_temperature_dependence_on_gamma`,
:py:attr:`maximum_series_resistance` and :py:attr:`maximum_recombination_parameter` (if applicable).

.. code-block:: python

    module.shunt_resistance_at_stc = 8000
    module.dark_shunt_resistance = 9000
    module.generate_single_diode_parameters_advanced()
    new_eir = module.calculate_effective_irradiance_response()

Once the user is satisfied with the module parameters and performance, assign other required fields.

.. code-block:: python

    from plantpredict.enumerations import ConstructionTypeEnum
    module.name = "Test Module"
    module.model = "Test Module"
    module.manufacturer = "Solar Company"
    module.length = 2009
    module.width = 1232
    module.heat_absorption_coef_alpha_t = 0.9
    module.construction_type = ConstructionTypeEnum.GLASS_GLASS

Create a new :py:mod:`~plantpredict.module.Module` in the PlantPredict database.

.. code-block:: python

    module.create()


Set a prediction's monthly factors (albedo, soiling loss, spectral loss).
---------------------------------------------------------------------------

Monthly albedo, soiling loss :py:data:`[%]`, and spectral loss :py:data:`[%]` can all be set for a prediction with the
attribute :py:attr:`monthly_factors` (a py:data:`dict`). This can be done upon initial creation of a prediction from
scratch (see the example for `Create Project and Prediction from scratch.`_), but for the sake of example, we will
consider the case of updating an existing prediction.

First instantiate the prediction of interest using the :py:class:`~plantpredict.prediction.Prediction` class, specifying
its :py:attr:`id` and :py:attr:`project_id` (visible in the URL of that prediction in a web browser
... :py:data:`/projects/{project_id}/prediction/{id}/`).

.. code-block:: python

    project_id = 13161  # CHANGE TO YOUR PROJECT ID
    prediction_id = 147813  # CHANGE TO YOUR PREDICTION ID
    prediction = api.prediction(id=prediction_id, project_id=project_id)

Retrieve the prediction's attributes.

.. code-block:: python

    prediction.get()

This example assumes that the user wants to specify all 3 available :py:attr:`monthly_factors`, and enforce that the
prediction use monthly soiling loss and spectral loss averages. (Alternatively, a user can choose to only specify
albedo, or albedo and soiling loss, or albedo and spectral shift.)

Set the :py:attr:`monthly_factors` as such, where albedo is in units :py:data:`[decimal]`, soiling loss in
:py:data:`[%]`, and spectral loss in :py:data:`[%]`. (Note: for soiling loss and spectral loss, a negative number
indicates a gain.) The values below should be replaced with those obtained from measurements or otherwise relevant to
the project being modeled.

.. code-block:: python

    prediction.monthly_factors = [
        {"month": 1, "month_name": "Jan", "albedo": 0.4, "soiling_loss": 0.40, "spectral_shift": 0.958},
        {"month": 2, "month_name": "Feb", "albedo": 0.3, "soiling_loss": 0.24, "spectral_shift": 2.48},
        {"month": 3, "month_name": "Mar", "albedo": 0.2, "soiling_loss": 0.76, "spectral_shift": 3.58},
        {"month": 4, "month_name": "Apr", "albedo": 0.2, "soiling_loss": 0.88, "spectral_shift": 3.48},
        {"month": 5, "month_name": "May", "albedo": 0.2, "soiling_loss": 0.81, "spectral_shift": 2.58},
        {"month": 6, "month_name": "Jun", "albedo": 0.2, "soiling_loss": 1.01, "spectral_shift": 1.94},
        {"month": 7, "month_name": "Jul", "albedo": 0.2, "soiling_loss": 1.21, "spectral_shift": 3.7},
        {"month": 8, "month_name": "Aug", "albedo": 0.2, "soiling_loss": 0.99, "spectral_shift": 4.57},
        {"month": 9, "month_name": "Sep", "albedo": 0.2, "soiling_loss": 1.34, "spectral_shift": 6.39},
        {"month": 10, "month_name": "Oct", "albedo": 0.2, "soiling_loss": 0.54, "spectral_shift": 4.16},
        {"month": 11, "month_name": "Nov", "albedo": 0.3, "soiling_loss": 0.52, "spectral_shift": 0.758},
        {"month": 12, "month_name": "Dec", "albedo": 0.4, "soiling_loss": 0.33, "spectral_shift": 0.886}
    ]

In order to enforce that the prediction use monthly average values (rather than soiling time series from a weather
file, for instance), the attributes :py:attr:`soiling_model` and :py:attr:`spectral_shift_model` must be set with the
following code (assuming that both soiling loss and spectral shift loss have been specified in
:py:attr:`monthly factors`).

.. code-block:: python

    from plantpredict.enumerations import SoilingModelTypeEnum, SpectralShiftModelEnum
    prediction.soiling_model = SoilingModelTypeEnum.CONSTANT_MONTHLY
    prediction.spectral_shift_model = SpectralShiftModelEnum.MONTHLY_OVERRIDE

Call the :py:meth:`~plantpredict.prediction.Prediction.update` method on the instance of
:py:class:`~plantpredict.prediction.Prediction` to persist these changes to PlantPredict.

.. code-block:: python

    prediction.update()

