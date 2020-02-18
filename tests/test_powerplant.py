import mock
import unittest

from tests import plantpredict_unit_test_case, mocked_requests
from tests.mocked_methods import mock_get_inverter_apparent_power, mock_get_inverter_kva_rating, \
    mock_calculate_default_post_height, mock_calculate_collector_bandwidth
from plantpredict.powerplant import PowerPlant
from plantpredict.enumerations import TrackingTypeEnum, ModuleOrientationEnum, BacktrackingTypeEnum


class TestPowerPlant(plantpredict_unit_test_case.PlantPredictUnitTestCase):

    @mock.patch('plantpredict.plant_predict_entity.PlantPredictEntity.create')
    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_and_set_average_power_factor')
    def test_create(self, mock_calculate_and_set_average_power_factor, mocked_create):
        self._make_mocked_api()
        powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)

        powerplant.create()
        self.assertEqual(powerplant.create_url_suffix, "/Project/7/Prediction/77/PowerPlant")
        self.assertTrue(mock_calculate_and_set_average_power_factor.called)
        self.assertTrue(mocked_create.called)
        self.assertEqual(powerplant.power_factor, 1.0)

    @mock.patch('plantpredict.plant_predict_entity.PlantPredictEntity.get')
    def test_get(self, mocked_get):
        self._make_mocked_api()
        powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)

        powerplant.get()
        self.assertEqual(powerplant.get_url_suffix, "/Project/7/Prediction/77/PowerPlant")
        self.assertTrue(mocked_get.called)

    @mock.patch('plantpredict.plant_predict_entity.PlantPredictEntity.update')
    def test_update(self, mocked_update):
        self._make_mocked_api()
        powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)

        powerplant.update()
        self.assertEqual(powerplant.update_url_suffix, "/Project/7/Prediction/77/PowerPlant")
        self.assertTrue(mocked_update.called)

    def _init_powerplant_structure(self):
        self.powerplant.blocks = [
            {"id": 1, "name": 1, "arrays": [
                {"id": 11, "name": 1, "inverters": [{"id": 111, "name": "A", "dc_fields": [{"id": 1111, "name": 1}]}]}
            ]}
        ]

    def test_calculate_sum_power_factors(self):
        self._make_mocked_api()
        powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        powerplant.blocks = [{
            'repeater': 1,
            'arrays': [
                {
                    'repeater': 1,
                    'inverters': [
                        {'repeater': 5, 'power_factor': 1.0},
                        {'repeater': 1, 'power_factor': 0.9},
                        {'repeater': 3, 'power_factor': 0.8}
                    ]
                },
                {
                    'repeater': 1,
                    'inverters': [
                        {'repeater': 6, 'power_factor': 0.96},
                        {'repeater': 2, 'power_factor': 1.0}
                    ]
                }
            ],
        }]

        sum_power_factors = powerplant._calculate_sum_power_factors()
        self.assertAlmostEqual(sum_power_factors, 16.06)

    def test_calculate_num_inverters(self):
        self._make_mocked_api()
        powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        powerplant.blocks = [
            {'arrays': [{'repeater': 1, 'inverters': [{'power_factor': 0.91703056769, 'repeater': 3}]}]},
            {'arrays': [{'repeater': 2, 'inverters': [{'power_factor': 1, 'repeater': 1}]}]},
            {'arrays': [{'repeater': 1, 'inverters': [{'power_factor': 0.95487627365, 'repeater': 1}]}]},
        ]

        num_inverters = powerplant._calculate_num_inverters()
        self.assertEqual(num_inverters, 6)

    def test_calculate_and_set_average_power_factor(self):
        self._make_mocked_api()
        powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        powerplant.blocks = [
            {'arrays': [{'repeater': 1, 'inverters': [{'power_factor': 0.91703056769, 'repeater': 3}]}]},
            {'arrays': [{'repeater': 2, 'inverters': [{'power_factor': 1, 'repeater': 1}]}]},
            {'arrays': [{'repeater': 1, 'inverters': [{'power_factor': 0.95487627365, 'repeater': 1}]}]},
        ]

        powerplant._calculate_and_set_average_power_factor()
        self.assertAlmostEqual(powerplant.power_factor, 0.9509946627850558)

    def test_calculate_and_set_average_power_factor_zero_inverters(self):
        self._make_mocked_api()
        powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        powerplant.blocks = [{'arrays': [{'inverters': []}, {'inverters': []}]}]

        powerplant._calculate_and_set_average_power_factor()
        self.assertEqual(powerplant.power_factor, 0)

    def test_add_transformer_first(self):
        """Tests adding a transformer to a power plant with no existing transformers."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_transformer(
            rating=0.6,
            high_side_voltage=600,
            no_load_loss=1.1,
            full_load_loss=1.7,
            ordinal=1
        )
        self.assertEqual(self.powerplant.transformers, [{
            "rating": 0.6,
            "high_side_voltage": 600,
            "no_load_loss": 1.1,
            "full_load_loss": 1.7,
            "ordinal": 1
        }])

    def test_add_transformer_multiple(self):
        """Tests adding a transformer to a power plant with existing transformers."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_transformer(rating=0.6, high_side_voltage=600, no_load_loss=1.1,
                                        full_load_loss=1.7, ordinal=1)
        self.powerplant.add_transformer(rating=0.6, high_side_voltage=600, no_load_loss=1.1,
                                        full_load_loss=1.7, ordinal=1)

        self.assertEqual(self.powerplant.transformers, [
            {"rating": 0.6, "high_side_voltage": 600, "no_load_loss": 1.1, "full_load_loss": 1.7, "ordinal": 1},
            {"rating": 0.6, "high_side_voltage": 600, "no_load_loss": 1.1, "full_load_loss": 1.7, "ordinal": 1}
        ])

    def test_add_transmission_line_first(self):
        """Tests adding a transmission line to a powerplant with no existing transmission lines."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_transmission_line(
            length=3.0,
            resistance=0.1,
            number_of_conductors_per_phase=1,
            ordinal=1
        )
        self.assertEqual(self.powerplant.transmission_lines, [{
            "length": 3.0,
            "resistance": 0.1,
            "number_of_conductors_per_phase": 1,
            "ordinal": 1
        }])

    def test_add_transmission_line_multiple(self):
        """Tests adding a transmission line to a powerplant with existing transmission lines."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_transmission_line(length=3.0, resistance=0.1, number_of_conductors_per_phase=1, ordinal=1)
        self.powerplant.add_transmission_line(length=3.0, resistance=0.1, number_of_conductors_per_phase=1, ordinal=1)
        self.assertEqual(self.powerplant.transmission_lines, [
            {"length": 3.0, "resistance": 0.1, "number_of_conductors_per_phase": 1, "ordinal": 1},
            {"length": 3.0, "resistance": 0.1, "number_of_conductors_per_phase": 1, "ordinal": 1}
        ])

    def test_clone_block(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()
        cloned_block_name = self.powerplant.clone_block(block_id_to_clone=1)

        self.assertIsNotNone(cloned_block_name)
        self.assertEqual(cloned_block_name, 2)
        self.assertEqual(len(self.powerplant.blocks), 2)
        self.assertEqual(self.powerplant.blocks[-1], {"id": 1, "name": 2, "arrays": [
                {"id": 11, "name": 1, "inverters": [{"id": 111, "name": "A", "dc_fields": [{"id": 1111, "name": 1}]}]}
            ]})

    def test_add_block_first_default_inputs(self):
        """Tests adding a block to a power plant with no existing plots, and all default inputs."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        block_name = self.powerplant.add_block()

        self.assertEqual(len(self.powerplant.blocks), 1)
        self.assertEqual(block_name, 1)
        self.assertEqual(self.powerplant.blocks[0], {
            "name": 1,
            "use_energization_date": False,
            "energization_date": "",
            "arrays": []
        })

    def test_add_block_first_non_default_inputs(self):
        """Tests adding a block to a power plant with no existing plots, and non-default inputs."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        block_name = self.powerplant.add_block(use_energization_date=True, energization_date='2018-01-01')

        self.assertEqual(len(self.powerplant.blocks), 1)
        self.assertEqual(block_name, 1)
        self.assertEqual(self.powerplant.blocks[0], {
            "name": 1,
            "use_energization_date": True,
            "energization_date": "2018-01-01",
            "arrays": []
        })

    def test_add_block_multiple(self):
        """Tests adding a block to a power plant with existing plots."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()
        block_name = self.powerplant.add_block()

        self.assertEqual(len(self.powerplant.blocks), 2)
        self.assertEqual(block_name, 2)
        self.assertEqual(self.powerplant.blocks[-1], {
            "name": 2,
            "use_energization_date": False,
            "energization_date": "",
            "arrays": []
        })

    def test_add_array_default_inputs(self):
        """Test adding array with all default inputs."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()
        array_name = self.powerplant.add_array(block_name=1, description="testing")

        self.assertEqual(len(self.powerplant.blocks[0]["arrays"]), 2)
        self.assertEqual(array_name, 2)
        self.assertEqual(self.powerplant.blocks[0]["arrays"][1], {
            "name": 2,
            "repeater": 1,
            "ac_collection_loss": 1,
            "das_load": 800,
            "cooling_load": 0,
            "additional_losses": 0,
            "transformer_enabled": True,
            "match_total_inverter_kva": True,
            "transformer_high_side_voltage": 34.5,
            "transformer_no_load_loss": 0.2,
            "transformer_full_load_loss": 0.7,
            "inverters": [],
            "description": "testing"
        })

    def test_validate_block_name(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        with self.assertRaises(ValueError):
            self.powerplant._validate_block_name(2)

    def test_add_array_invalid_block_name(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        with self.assertRaises(ValueError):
            self.powerplant.add_array(block_name=2, description="testing")

    def test_add_array_non_default_inputs(self):
        """Test add array with all non default inputs, including False for match_total_inverter_kva."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()
        array_name = self.powerplant.add_array(
            block_name=1,
            transformer_enabled=False,
            match_total_inverter_kva=False,
            transformer_kva_rating=700.0,
            repeater=2,
            ac_collection_loss=2,
            das_load=900,
            cooling_load=0.1,
            additional_losses=0.2,
            transformer_high_side_voltage=35.0,
            transformer_no_load_loss=0.3,
            transformer_full_load_loss=0.8,
            description="testing"

        )

        self.assertEqual(len(self.powerplant.blocks[0]["arrays"]), 2)
        self.assertEqual(array_name, 2)
        self.assertEqual(self.powerplant.blocks[0]["arrays"][1], {
            "name": 2,
            "repeater": 2,
            "ac_collection_loss": 2,
            "das_load": 900,
            "cooling_load": 0.1,
            "additional_losses": 0.2,
            "transformer_enabled": False,
            "match_total_inverter_kva": False,
            "transformer_high_side_voltage": 35,
            "transformer_no_load_loss": 0.3,
            "transformer_full_load_loss": 0.8,
            "inverters": [],
            "description": "testing",
            "transformer_kva_rating": 700.0
        })

    def test_validate_array_name_invalid_block(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        try:
            self.powerplant._validate_array_name(block_name=2, array_name=3)
        except ValueError as e:
            self.assertEqual(e.args[0], "2 is not a valid block name in the existing power plant structure.")

    def test_validate_array_name_invalid_array(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        try:
            self.powerplant._validate_array_name(block_name=1, array_name=3)
        except ValueError as e:
            self.assertEqual(e.args[0], "3 is not a valid array name in block 1.")

    def test_validate_inverter_setpoint_inputs_setpoint_none(self):
        """Tests _validate_inverter_setpoint_inputs when setpoint_kw is None."""
        setpoint_kw, power_factor = PowerPlant._validate_inverter_setpoint_inputs(
            setpoint_kw=None,
            power_factor=1.2,
            kva_rating=600
        )
        self.assertEqual(setpoint_kw, 720)
        self.assertEqual(power_factor, 1.2)

    def test_validate_inverter_setpoint_inputs_setpoint_provided_power_factor_1(self):
        """Tests _validate_inverter_setpoint_inputs when setpoint_kw is None."""
        setpoint_kw, power_factor = PowerPlant._validate_inverter_setpoint_inputs(
            setpoint_kw=800,
            power_factor=1.0,
            kva_rating=1000
        )
        self.assertEqual(setpoint_kw, 800)
        self.assertEqual(power_factor, 0.8)

    def test_validate_inverter_setpoint_inputs_invalid_inputs(self):
        with self.assertRaises(ValueError):
            PowerPlant._validate_inverter_setpoint_inputs(
                setpoint_kw=800,
                power_factor=1.2,
                kva_rating=1000
            )

    @mock.patch('plantpredict.powerplant.PowerPlant._get_inverter_apparent_power', mock_get_inverter_apparent_power)
    @mock.patch('plantpredict.powerplant.PowerPlant._get_inverter_kva_rating', mock_get_inverter_kva_rating)
    def test_add_inverter_default_inputs_use_cooling_temp(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self.powerplant.use_cooling_temp = True
        self._init_powerplant_structure()

        inverter_name = self.powerplant.add_inverter(block_name=1, array_name=1, inverter_id=123)
        self.assertEqual(len(self.powerplant.blocks[0]["arrays"][0]["inverters"]), 2)
        self.assertEqual(inverter_name, "B")
        self.assertEqual(self.powerplant.blocks[0]["arrays"][0]["inverters"][1], {
            "name": "B",
            "repeater": 1,
            "inverter_id": 123,
            "setpoint_kw": 900,
            "power_factor": 1.0,
            "kva_rating": 900.0,
            "dc_fields": []
        })

    @mock.patch('plantpredict.powerplant.PowerPlant._get_inverter_apparent_power', mock_get_inverter_apparent_power)
    @mock.patch('plantpredict.powerplant.PowerPlant._get_inverter_kva_rating', mock_get_inverter_kva_rating)
    def test_add_inverter_invalid_array_name(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self.powerplant.use_cooling_temp = True
        self._init_powerplant_structure()

        with self.assertRaises(ValueError):
            self.powerplant.add_inverter(block_name=1, array_name=3, inverter_id=123)

    @mock.patch('plantpredict.powerplant.PowerPlant._get_inverter_apparent_power', mock_get_inverter_apparent_power)
    def test_add_inverter_non_default_inputs_no_use_cooling_temp(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self.powerplant.use_cooling_temp = False
        self._init_powerplant_structure()
        inverter_name = self.powerplant.add_inverter(
            block_name=1, array_name=1, inverter_id=123, setpoint_kw=800
        )

        self.assertEqual(len(self.powerplant.blocks[0]["arrays"][0]["inverters"]), 2)
        self.assertEqual(inverter_name, "B")
        self.assertEqual(self.powerplant.blocks[0]["arrays"][0]["inverters"][1], {
            "name": "B",
            "repeater": 1,
            "inverter_id": 123,
            "setpoint_kw": 800,
            "power_factor": 1.0,
            "kva_rating": 800.0,
            "dc_fields": []
        })

    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    def test_get_default_module_azimuth_from_latitude_above_equator(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)

        default_module_azimuth = self.powerplant._get_default_module_azimuth_from_latitude()
        self.assertEqual(default_module_azimuth, 180.0)

    def test_calculate_collector_bandwidth_portrait(self):
        collector_bandwidth = PowerPlant._calculate_collector_bandwidth(
            module_length=1960,
            module_width=992,
            module_orientation=ModuleOrientationEnum.PORTRAIT,
            modules_high=4,
            vertical_intermodule_gap=0.02
        )
        self.assertAlmostEqual(collector_bandwidth, 7.90, 2)

    def test_calculate_collector_bandwidth_landscape(self):
        collector_bandwidth = PowerPlant._calculate_collector_bandwidth(
            module_length=1960,
            module_width=992,
            module_orientation=ModuleOrientationEnum.LANDSCAPE,
            modules_high=4,
            vertical_intermodule_gap=0.02
        )
        self.assertAlmostEqual(collector_bandwidth, 4.03, 2)

    def test_calculate_table_length_portrait(self):
        table_length = PowerPlant._calculate_table_length(
            modules_wide=18,
            module_orientation=ModuleOrientationEnum.PORTRAIT,
            module_length=1960,
            module_width=992,
            lateral_intermodule_gap=0.02
        )
        self.assertEqual(table_length, 18.196)

    def test_calculate_table_length_landscape(self):
        table_length = PowerPlant._calculate_table_length(
            modules_wide=18,
            module_orientation=ModuleOrientationEnum.LANDSCAPE,
            module_length=1960,
            module_width=992,
            lateral_intermodule_gap=0.02
        )
        self.assertAlmostEqual(table_length, 35.62)

    def test_calculate_tables_per_row(self):
        tables_per_row = PowerPlant._calculate_tables_per_row(
            field_dc_power=756,
            planned_module_rating=360,
            modules_high=4,
            modules_wide=18,
            number_of_rows=10
        )
        self.assertEqual(tables_per_row, 3)

    def test_calculate_tables_per_row_with_tables_removed(self):
        tables_per_row = PowerPlant._calculate_tables_per_row(
            field_dc_power=756,
            planned_module_rating=360,
            modules_high=4,
            modules_wide=18,
            number_of_rows=10,
            tables_removed_for_pcs=1.0,

        )
        self.assertEqual(tables_per_row, 4)

    def test_calculate_dc_field_size_by_collector_bandwidth(self):
        dc_field_size = PowerPlant._calculate_dc_field_size_by_collector_bandwidth(
            number_of_rows=10,
            post_to_post_spacing=9.799999999999997,
            collector_bandwidth=4.03
        )
        self.assertAlmostEqual(dc_field_size, 92.23, 2)

    def test_calculate_dc_field_size_by_tables_per_row_landscape_module_orientation(self):
        dc_field_size = PowerPlant._calculate_dc_field_size_by_tables_per_row(
            tables_per_row=2.8463,
            module_orientation=ModuleOrientationEnum.LANDSCAPE,
            module_length=1960,
            module_width=992,
            lateral_intermodule_gap=0.02,
            modules_wide=18
        )
        self.assertAlmostEqual(dc_field_size, 101.42, 2)

    def test_calculate_dc_field_size_by_tables_per_row_portrait_module_orientation(self):
        dc_field_size = PowerPlant._calculate_dc_field_size_by_tables_per_row(
            tables_per_row=4,
            module_orientation=ModuleOrientationEnum.PORTRAIT,
            module_length=1960,
            module_width=992,
            lateral_intermodule_gap=0.02,
            modules_wide=18
        )
        self.assertAlmostEqual(dc_field_size, 72.86, 1)

    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_dc_field_size_by_tables_per_row')
    def test_calculate_dc_field_length_tracker(self, mock_calculate_dc_field_size_by_tables_per_row):
        self._make_mocked_api()
        powerplant = PowerPlant(self.mocked_api)
        powerplant._calculate_dc_field_length(2, ModuleOrientationEnum.PORTRAIT, 1962, 900, 0.02, 18,
                                              TrackingTypeEnum.HORIZONTAL_TRACKER, 1, 1.5, 4.03)
        self.assertTrue(mock_calculate_dc_field_size_by_tables_per_row.called)

    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_dc_field_size_by_collector_bandwidth')
    def test_calculate_dc_field_length_fixed_tilt(self, mock_calculate_dc_field_size_by_collector_bandwidth):
        self._make_mocked_api()
        powerplant = PowerPlant(self.mocked_api)
        powerplant._calculate_dc_field_length(2, ModuleOrientationEnum.PORTRAIT, 1962, 900, 0.02, 18,
                                              TrackingTypeEnum.FIXED_TILT, 1, 1.5, 4.03)
        self.assertTrue(mock_calculate_dc_field_size_by_collector_bandwidth.called)

    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_dc_field_size_by_collector_bandwidth')
    def test_calculate_dc_field_width_tracker(self, mock_calculate_dc_field_size_by_collector_bandwidth):
        self._make_mocked_api()
        powerplant = PowerPlant(self.mocked_api)
        powerplant._calculate_dc_field_width(TrackingTypeEnum.HORIZONTAL_TRACKER, 1, 1.5, 4.03, 2,
                                             ModuleOrientationEnum.PORTRAIT, 1962, 900, 0.02, 18)
        self.assertTrue(mock_calculate_dc_field_size_by_collector_bandwidth.called)

    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_dc_field_size_by_tables_per_row')
    def test_calculate_dc_field_width_fixed_tilt(self, mock_calculate_dc_field_size_by_tables_per_row):
        self._make_mocked_api()
        powerplant = PowerPlant(self.mocked_api)
        powerplant._calculate_dc_field_width(TrackingTypeEnum.FIXED_TILT, 1, 1.5, 4.03, 2,
                                             ModuleOrientationEnum.PORTRAIT, 1962, 900, 0.02, 18)
        self.assertTrue(mock_calculate_dc_field_size_by_tables_per_row.called)

    def test_validate_dc_field_sizing_both_specified(self):
        try:
            PowerPlant._validate_dc_field_sizing(
                field_dc_power=869.4,
                number_of_series_strings_wired_in_parallel=420.0,
                modules_wired_in_series=6,
                planned_module_rating=420.0
            )
        except ValueError as e:
            self.assertEqual(e.args[0], "Both field_dc_power and number_of_series_strings_wired_in_parallel are not "
                                        "None. Only one of these values can be specified (and the other will be "
                                        "calculated).")

    def test_validate_dc_field_sizing_with_field_dc_power(self):
        field_dc_power, number_of_series_strings_wired_in_parallel = PowerPlant._validate_dc_field_sizing(
            field_dc_power=869.4,
            number_of_series_strings_wired_in_parallel=None,
            modules_wired_in_series=6,
            planned_module_rating=420.0
        )
        self.assertEqual(field_dc_power, 869.4)
        self.assertEqual(number_of_series_strings_wired_in_parallel, 345.0)

    def test_validate_dc_field_sizing_with_number_of_series_strings_wired_in_parallel(self):
        field_dc_power, number_of_series_strings_wired_in_parallel = PowerPlant._validate_dc_field_sizing(
            field_dc_power=None,
            number_of_series_strings_wired_in_parallel=345.0,
            modules_wired_in_series=6,
            planned_module_rating=420.0
        )
        self.assertEqual(field_dc_power, 869.4)
        self.assertEqual(number_of_series_strings_wired_in_parallel, 345.0)

    def test_validate_dc_field_sizing_neither_specified(self):
        try:
            PowerPlant._validate_dc_field_sizing(
                field_dc_power=None,
                number_of_series_strings_wired_in_parallel=None,
                modules_wired_in_series=6,
                planned_module_rating=420.0
            )
        except ValueError as e:
            self.assertEqual(e.args[0], "Both field_dc_power and number_of_series_strings_wired_in_parallel are None. "
                                        "One of these variables must be specified, and the other will be calculated.")

    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_collector_bandwidth',
                new=mock_calculate_collector_bandwidth)
    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    def test_calculate_post_to_post_spacing_from_gcr(self):
        self._make_mocked_api()
        powerplant = PowerPlant(self.mocked_api)
        post_to_post_spacing = powerplant.calculate_post_to_post_spacing_from_gcr(
            ground_coverage_ratio=0.40,
            module_id=123,
            modules_high=4
        )
        self.assertAlmostEqual(post_to_post_spacing, 4.175, 3)

    def test_calculate_field_dc_power(self):
        field_dc_power = PowerPlant.calculate_field_dc_power_from_dc_ac_ratio(
            dc_ac_ratio=1.20,
            inverter_setpoint=630
        )
        self.assertEqual(field_dc_power, 756)

    def test_validate_mounting_structure_parameters_fixed_tilt_valid(self):
        PowerPlant._validate_mounting_structure_parameters(
            tracking_type=TrackingTypeEnum.FIXED_TILT,
            module_tilt=30.0,
            tracking_backtracking_type=None
        )

    def test_validate_mounting_structure_parameters_fixed_tilt_invalid(self):
        with self.assertRaises(ValueError) as e:
            PowerPlant._validate_mounting_structure_parameters(
                tracking_type=TrackingTypeEnum.FIXED_TILT,
                module_tilt=None,
                tracking_backtracking_type=None
            )

        self.assertEqual(e.exception.args[0], "The input module_tilt is required for a fixed tilt DC field.")

    def test_validate_mounting_structure_parameters_tracking_true_tracking_valid(self):
        PowerPlant._validate_mounting_structure_parameters(
            tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
            module_tilt=None,
            tracking_backtracking_type=BacktrackingTypeEnum.TRUE_TRACKING
        )

    def test_validate_mounting_structure_parameters_tracking_backtracking_valid(self):
        PowerPlant._validate_mounting_structure_parameters(
            tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
            module_tilt=None,
            tracking_backtracking_type=BacktrackingTypeEnum.BACKTRACKING
        )

    def test_validate_mounting_structure_parameters_tracking_invalid(self):
        with self.assertRaises(ValueError) as e:
            PowerPlant._validate_mounting_structure_parameters(
                tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
                module_tilt=None,
                tracking_backtracking_type=None
            )

        self.assertEqual(e.exception.args[0], "The input tracking_backtracking_type is required for a horizontal "
                                              "tracker DC field.")

    def test_validate_inverter_name_invalid_block(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        try:
            self.powerplant._validate_inverter_name(block_name=2, array_name=3, inverter_name='B')
        except ValueError as e:
            self.assertEqual(e.args[0], "2 is not a valid block name in the existing power plant structure.")

    def test_validate_inverter_name_invalid_array(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        try:
            self.powerplant._validate_inverter_name(block_name=1, array_name=3, inverter_name='B')
        except ValueError as e:
            self.assertEqual(e.args[0], "3 is not a valid array name in block 1.")

    def test_validate_inverter_name_invalid_inverter_name(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        try:
            self.powerplant._validate_inverter_name(block_name=1, array_name=1, inverter_name='B')
        except ValueError as e:
            self.assertEqual(e.args[0], "'B' is not a valid inverter name in array 1 of block 1.")

    def test_calculate_default_post_height_less_than_1pt5meters(self):
        """Tests that 1.5 is returned if calculated post height is less than 1.5"""
        post_height = PowerPlant._calculate_default_post_height(
            tracking_type=TrackingTypeEnum.FIXED_TILT,
            collector_bandwidth=1.5,
            module_tilt=30,
            minimum_tracking_limit_angle_d=-60,
            maximum_tracking_limit_angle_d=60
        )

        self.assertEqual(post_height, 1.5)

    def test_calculate_default_post_height_fixed_tilt(self):
        post_height = PowerPlant._calculate_default_post_height(
            tracking_type=TrackingTypeEnum.FIXED_TILT,
            collector_bandwidth=3.0,
            module_tilt=30,
            minimum_tracking_limit_angle_d=-60,
            maximum_tracking_limit_angle_d=60
        )

        self.assertEqual(post_height, 1.75)

    def test_calculate_default_post_height_tracker(self):
        post_height = PowerPlant._calculate_default_post_height(
            tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
            collector_bandwidth=3.0,
            module_tilt=30,
            minimum_tracking_limit_angle_d=-60,
            maximum_tracking_limit_angle_d=60
        )

        self.assertEqual(post_height, 2.299038105676658)

    def test_calculate_modules_wide(self):
        modules_wide = PowerPlant._calculate_modules_wide(strings_wide=3, modules_wired_in_series=6)

        self.assertEqual(modules_wide, 18)

    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_default_post_height', mock_calculate_default_post_height)
    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    def test_add_dc_field_with_bifacial_default_inputs(self):
        self._make_mocked_api(module_id=456)
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_dc_field(
            block_name=1,
            array_name=1,
            inverter_name="A",
            module_id=456,
            tracking_type=TrackingTypeEnum.FIXED_TILT,
            number_of_series_strings_wired_in_parallel=400,
            modules_high=4,
            modules_wired_in_series=10,
            post_to_post_spacing=1.0,
            module_tilt=30,
        )

        self.assertEqual(self.powerplant.blocks[0]["arrays"][0]["inverters"][0]["dc_fields"][1], {
            "name": 2,
            "module_id": 456,
            "tracking_type": TrackingTypeEnum.FIXED_TILT,
            "module_tilt": 30,
            "minimum_tracking_limit_angle_d": -60.0,
            "maximum_tracking_limit_angle_d": 60.0,
            "module_orientation": ModuleOrientationEnum.LANDSCAPE,
            "modules_high": 4,
            "module_azimuth": 180.0,
            "collector_bandwidth": 4.859999999999999,
            "post_to_post_spacing": 1.0,
            "planned_module_rating": 120,
            "modules_wired_in_series": 10,
            "field_dc_power": 480.0,
            "number_of_series_strings_wired_in_parallel": 400,
            "module_count": 4000.0,
            "module_quality": 1.0,
            "module_mismatch_coefficient": 1.0,
            "light_induced_degradation": 1.0,
            "dc_wiring_loss_at_stc": 1.5,
            "dc_health": 1.0,
            "heat_balance_conductive_coef": -3.47,
            "heat_balance_convective_coef": -0.0594,
            "sandia_conductive_coef": 30.7,
            "cell_to_module_temp_diff": 3.0,
            "sandia_convective_coef": 0.0,
            "tracker_load_loss": 0.0,
            "lateral_intermodule_gap": 0.02,
            "vertical_intermodule_gap": 0.02,
            "modules_wide": 10,
            "table_to_table_spacing": 0.0,
            "number_of_rows": 1,
            "table_length": 20.18,
            "tables_per_row": 100,
            'field_length': 4.859999999999999,
            'field_width': 2019.98,
            'post_height': 2.234,
            'structure_shading': 0.0,
            'backside_mismatch': 3.0
        })

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    def test_add_dc_field_with_bifacial_non_default_inputs(self):
        self._make_mocked_api(module_id=456)
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_dc_field(
            block_name=1,
            array_name=1,
            inverter_name="A",
            module_id=456,
            tracking_type=TrackingTypeEnum.FIXED_TILT,
            number_of_series_strings_wired_in_parallel=400,
            modules_high=4,
            modules_wired_in_series=10,
            post_to_post_spacing=1.0,
            module_tilt=30,
            post_height=1.5,
            structure_shading=1.0,
            backside_mismatch=2.0
        )

        self.assertEqual(self.powerplant.blocks[0]["arrays"][0]["inverters"][0]["dc_fields"][1], {
            "name": 2,
            "module_id": 456,
            "tracking_type": TrackingTypeEnum.FIXED_TILT,
            "module_tilt": 30,
            "minimum_tracking_limit_angle_d": -60.0,
            "maximum_tracking_limit_angle_d": 60.0,
            "module_orientation": ModuleOrientationEnum.LANDSCAPE,
            "modules_high": 4,
            "module_azimuth": 180.0,
            "collector_bandwidth": 4.859999999999999,
            "post_to_post_spacing": 1.0,
            "planned_module_rating": 120,
            "modules_wired_in_series": 10,
            "field_dc_power": 480.0,
            "number_of_series_strings_wired_in_parallel": 400,
            "module_count": 4000.0,
            "module_quality": 1.0,
            "module_mismatch_coefficient": 1.0,
            "light_induced_degradation": 1.0,
            "dc_wiring_loss_at_stc": 1.5,
            "dc_health": 1.0,
            "heat_balance_conductive_coef": -3.47,
            "heat_balance_convective_coef": -0.0594,
            "sandia_conductive_coef": 30.7,
            "cell_to_module_temp_diff": 3.0,
            "sandia_convective_coef": 0.0,
            "tracker_load_loss": 0.0,
            "lateral_intermodule_gap": 0.02,
            "vertical_intermodule_gap": 0.02,
            "modules_wide": 10,
            "table_to_table_spacing": 0.0,
            "number_of_rows": 1,
            "table_length": 20.18,
            "tables_per_row": 100.0,
            'field_length': 4.859999999999999,
            'field_width': 2019.98,
            'post_height': 1.5,
            'structure_shading': 1.0,
            'backside_mismatch': 2.0
        })

    def test_add_dc_field_seasonal_tilt(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        with self.assertRaises(ValueError):
            self.powerplant.add_dc_field(
                block_name=1,
                array_name=1,
                inverter_name="A",
                module_id=123,
                tracking_type=TrackingTypeEnum.SEASONAL_TILT,
                number_of_series_strings_wired_in_parallel=400,
                modules_high=4,
                modules_wired_in_series=10,
                post_to_post_spacing=1.0,
                module_tilt=30
            )

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    def test_add_dc_field_fixed_tilt(self):
        """Test minimum inputs for successfully adding fixed tilt DC field."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        dc_field_name = self.powerplant.add_dc_field(
            block_name=1,
            array_name=1,
            inverter_name="A",
            module_id=123,
            tracking_type=TrackingTypeEnum.FIXED_TILT,
            number_of_series_strings_wired_in_parallel=400,
            modules_high=4,
            modules_wired_in_series=10,
            post_to_post_spacing=1.0,
            module_tilt=30
        )

        self.assertEqual(len(self.powerplant.blocks[0]["arrays"][0]["inverters"][0]["dc_fields"][0]), 2)
        self.assertEqual(dc_field_name, 2)
        self.assertEqual(self.powerplant.blocks[0]["arrays"][0]["inverters"][0]["dc_fields"][1], {
            "name": 2,
            "module_id": 123,
            "tracking_type": TrackingTypeEnum.FIXED_TILT,
            "module_tilt": 30,
            "minimum_tracking_limit_angle_d": -60.0,
            "maximum_tracking_limit_angle_d": 60.0,
            "module_orientation": ModuleOrientationEnum.LANDSCAPE,
            "modules_high": 4,
            "module_azimuth": 180.0,
            "collector_bandwidth": 4.859999999999999,
            "post_to_post_spacing": 1.0,
            "planned_module_rating": 120,
            "modules_wired_in_series": 10,
            "field_dc_power": 480.0,
            "number_of_series_strings_wired_in_parallel": 400,
            "module_count": 4000.0,
            "module_quality": 1.0,
            "module_mismatch_coefficient": 1.0,
            "light_induced_degradation": 1.0,
            "dc_wiring_loss_at_stc": 1.5,
            "dc_health": 1.0,
            "heat_balance_conductive_coef": -3.47,
            "heat_balance_convective_coef": -0.0594,
            "sandia_conductive_coef": 30.7,
            "cell_to_module_temp_diff": 3.0,
            "sandia_convective_coef": 0.0,
            "tracker_load_loss": 0.0,
            "lateral_intermodule_gap": 0.02,
            "vertical_intermodule_gap": 0.02,
            "modules_wide": 10,
            "table_to_table_spacing": 0.0,
            "number_of_rows": 1,
            "table_length": 20.18,
            "tables_per_row": 100.0,
            'field_length': 4.859999999999999,
            'field_width': 2019.98,
            'post_height': 2.215,
        })

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    def test_add_dc_field_tracking(self):
        """Test minimum inputs for successfully adding tracker DC field."""
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        dc_field_name = self.powerplant.add_dc_field(
            block_name=1,
            array_name=1,
            inverter_name="A",
            module_id=123,
            tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
            number_of_series_strings_wired_in_parallel=400,
            modules_high=4,
            modules_wired_in_series=10,
            post_to_post_spacing=1.0,
            tracking_backtracking_type=BacktrackingTypeEnum.BACKTRACKING
        )

        self.assertEqual(len(self.powerplant.blocks[0]["arrays"][0]["inverters"][0]["dc_fields"][0]), 2)
        self.assertEqual(dc_field_name, 2)
        self.assertEqual(self.powerplant.blocks[0]["arrays"][0]["inverters"][0]["dc_fields"][1], {
            "name": 2,
            "module_id": 123,
            "tracking_type": TrackingTypeEnum.HORIZONTAL_TRACKER,
            "tracking_backtracking_type": BacktrackingTypeEnum.BACKTRACKING,
            "minimum_tracking_limit_angle_d": -60.0,
            "maximum_tracking_limit_angle_d": 60.0,
            "module_orientation": ModuleOrientationEnum.LANDSCAPE,
            "modules_high": 4,
            "module_azimuth": 180.0,
            "collector_bandwidth": 4.859999999999999,
            "post_to_post_spacing": 1.0,
            "planned_module_rating": 120,
            "modules_wired_in_series": 10,
            "field_dc_power": 480.0,
            "number_of_series_strings_wired_in_parallel": 400,
            "module_count": 4000.0,
            "module_quality": 1.0,
            "module_mismatch_coefficient": 1.0,
            "light_induced_degradation": 1.0,
            "dc_wiring_loss_at_stc": 1.5,
            "dc_health": 1.0,
            "heat_balance_conductive_coef": -3.47,
            "heat_balance_convective_coef": -0.0594,
            "sandia_conductive_coef": 30.7,
            "cell_to_module_temp_diff": 3.0,
            "sandia_convective_coef": 0.0,
            "tracker_load_loss": 0.0,
            "lateral_intermodule_gap": 0.02,
            "vertical_intermodule_gap": 0.02,
            "modules_wide": 10,
            "table_to_table_spacing": 0.0,
            "number_of_rows": 1,
            "table_length": 20.18,
            "tables_per_row": 100,
            'field_length': 2019.98,
            'field_width': 4.859999999999999,
            'post_height': 3.1044417311961854,
        })

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.powerplant.PowerPlant._validate_dc_field_sizing')
    @mock.patch('plantpredict.powerplant.PowerPlant._validate_mounting_structure_parameters')
    @mock.patch('plantpredict.powerplant.PowerPlant._validate_inverter_name')
    def test_add_dc_field_validation_methods_called(self, mock_validate_inverter_name,
                                                    mock_validate_mounting_structure_parameters,
                                                    mock_validate_dc_field_sizing):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        try:
            self.powerplant.add_dc_field(
                block_name=1,
                array_name=1,
                inverter_name="A",
                module_id=123,
                tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
                number_of_series_strings_wired_in_parallel=400,
                modules_high=4,
                modules_wired_in_series=10,
                post_to_post_spacing=1.0,
                tracking_backtracking_type=BacktrackingTypeEnum.BACKTRACKING
            )
        except ValueError:
            pass

        self.assertTrue(mock_validate_inverter_name.called)
        self.assertTrue(mock_validate_mounting_structure_parameters.called)
        self.assertTrue(mock_validate_dc_field_sizing.called)

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_tables_per_row')
    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_table_length')
    @mock.patch('plantpredict.powerplant.PowerPlant._get_default_module_azimuth_from_latitude')
    def test_add_dc_field_helper_methods_called(self, mock_get_default_module_azimuth_from_latitude,
                                                mock_calculate_table_length, mock_calculate_tables_per_row):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_dc_field(
            block_name=1,
            array_name=1,
            inverter_name="A",
            module_id=123,
            tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
            number_of_series_strings_wired_in_parallel=400,
            modules_high=4,
            modules_wired_in_series=10,
            post_to_post_spacing=1.0,
            tracking_backtracking_type=BacktrackingTypeEnum.BACKTRACKING,
        )

        self.assertTrue(mock_get_default_module_azimuth_from_latitude.called)
        self.assertTrue(mock_calculate_table_length.called)
        self.assertTrue(mock_calculate_tables_per_row.called)

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_dc_field_width')
    @mock.patch('plantpredict.powerplant.PowerPlant._calculate_dc_field_length')
    def test_add_dc_field_dimension_calculator_helpers_called(self, mock_calculate_dc_field_length,
                                                              mock_calculate_dc_field_width):

        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        self.powerplant.add_dc_field(
            block_name=1,
            array_name=1,
            inverter_name="A",
            module_id=123,
            tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
            number_of_series_strings_wired_in_parallel=400,
            modules_high=4,
            modules_wired_in_series=10,
            post_to_post_spacing=1.0,
            tracking_backtracking_type=BacktrackingTypeEnum.BACKTRACKING,
            module_azimuth=180.0
        )

        self.assertTrue(mock_calculate_dc_field_length.called)
        self.assertTrue(mock_calculate_dc_field_width.called)

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    def test_add_dc_field_fails_on_fixed_tilt_no_module_tilt(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        with self.assertRaises(ValueError):
            self.powerplant.add_dc_field(
                block_name=1,
                array_name=1,
                inverter_name="A",
                module_id=123,
                field_dc_power=800,
                tracking_type=TrackingTypeEnum.FIXED_TILT,
                modules_high=4,
                modules_wired_in_series=10,
                post_to_post_spacing=1.5
            )

    @mock.patch('plantpredict.plant_predict_entity.requests.get', new=mocked_requests.mocked_requests_get)
    @mock.patch('plantpredict.project.requests.get', new=mocked_requests.mocked_requests_get)
    def test_add_dc_field_fails_on_tracker_no_backtracking_type(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77)
        self._init_powerplant_structure()

        with self.assertRaises(ValueError):
            self.powerplant.add_dc_field(
                block_name=1,
                array_name=1,
                inverter_name="A",
                module_id=123,
                number_of_series_strings_wired_in_parallel=400,
                tracking_type=TrackingTypeEnum.HORIZONTAL_TRACKER,
                modules_high=4,
                modules_wired_in_series=10,
                post_to_post_spacing=1.5
            )

    def test_init(self):
        self._make_mocked_api()
        self.powerplant = PowerPlant(api=self.mocked_api, project_id=7, prediction_id=77, some_kwarg='kwarg')

        self.assertEqual(self.powerplant.project_id, 7)
        self.assertEqual(self.powerplant.prediction_id, 77)
        self.assertTrue(self.powerplant.use_cooling_temp)
        self.assertEqual(self.powerplant.power_factor, 1.0)
        self.assertEqual(self.powerplant.blocks, [])
        self.assertEqual(self.powerplant.transformers, [])
        self.assertEqual(self.powerplant.transmission_lines, [])
        self.assertEqual(self.powerplant.some_kwarg, 'kwarg')


if __name__ == '__main__':
    unittest.main()
