import sys
import os

from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry, QgsPointXY
from qgis.testing import unittest
from parameterized import parameterized
from unittest.mock import patch, MagicMock

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.utils import install_package
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.constants import (
    FIRST_ALGO_NAME,
    SECOND_ALGO_NAME,
    PLUGIN_NAME
)
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.BaseTest import BaseTest
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.utils import (
    load_project,
    select_layer
)
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.racetrack_module import RacetrackModule, FlightParameters


class TestRacetracks(BaseTest):
    racetrack_module: RacetrackModule

    def setUp(self):
        super().setUp()
        self.racetrack_module = self.plugin_instance.racetrack_module
        
        # Mock the CRS and other settings for testing
        QgsProject.instance().writeEntry(PLUGIN_NAME, "max_turn_distance", 1000)

    @patch("ScienceFlightPlanner.racetrack_module.QFileDialog.getSaveFileName")
    def test_get_save_file_path(self, mock_save_dialog):
        # Arrange
        test_path = "/tmp/test.shp"
        mock_save_dialog.return_value = (test_path, "")
        
        # Act
        file_path = self.racetrack_module._get_save_file_path(
            "/tmp/input.shp", "TestSensor", 100.0, 0.5, 1000
        )
        
        # Assert
        self.assertEqual(file_path, test_path)
        mock_save_dialog.assert_called_once()

    @patch("ScienceFlightPlanner.racetrack_module.RacetrackDialog")
    @patch("ScienceFlightPlanner.racetrack_module.RacetrackModule._get_sensor_parameters")
    def test_get_flight_parameters(self, mock_get_sensor, mock_dialog):
        # Arrange
        mock_get_sensor.return_value = ("TestSensor", 45.0)
        
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.exec_.return_value = mock_dialog_instance.Accepted
        mock_dialog_instance.get_values.return_value = (1000, FIRST_ALGO_NAME)
        mock_dialog.return_value = mock_dialog_instance
        
        # Mock flight altitude spinbox
        self.racetrack_module.flight_altitude_spinbox = MagicMock()
        self.racetrack_module.flight_altitude_spinbox.value.return_value = 100
        
        # Mock coverage module computation
        self.racetrack_module.coverage_module.compute_sensor_coverage_in_meters = MagicMock()
        self.racetrack_module.coverage_module.compute_sensor_coverage_in_meters.return_value = 500
        
        # Mock settings
        self.racetrack_module.settings = MagicMock()
        self.racetrack_module.settings.value.return_value = 0.25
        
        # Act
        result = self.racetrack_module._get_flight_parameters()
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.flight_altitude, 100)
        self.assertEqual(result.sensor_name, "TestSensor")
        self.assertEqual(result.coverage_range, 500)
        self.assertEqual(result.max_turn_distance, 1000)
        self.assertEqual(result.algorithm, FIRST_ALGO_NAME)

    @parameterized.expand([
        ["meander_algorithm", FIRST_ALGO_NAME],
        ["racetrack_algorithm", SECOND_ALGO_NAME],
    ])
    @patch("ScienceFlightPlanner.racetrack_module.RacetrackModule._save_points_to_layer")
    @patch("ScienceFlightPlanner.racetrack_module.RacetrackModule.generate_points_shp_file")
    @patch("ScienceFlightPlanner.racetrack_module.RacetrackModule._prepare_computation_parameters")
    def test_compute_way_points(self, name, algorithm, mock_prepare_params, mock_generate_shp, mock_save_points):
        # Arrange
        flight_params = FlightParameters(
            flight_altitude=100.0,
            overlap=0.25,
            coverage_range=500.0,
            sensor_name="TestSensor",
            max_turn_distance=1000.0,
            algorithm=algorithm
        )
        
        # Mock input params
        mock_params = {
            'layer': MagicMock(),
            'feature': MagicMock(),
            'crs': MagicMock(),
            'coverage_crs': MagicMock(),
            'vec': MagicMock(),
            'vec_normalized': MagicMock(),
            'point_start': QgsPointXY(0, 0),
            'point_end': QgsPointXY(1000, 0),
            'coverage_range': 500.0,
            'overlap_factor': 0.75,
            'max_turn_distance': 1000.0,
            'flight_params': flight_params
        }
        
        mock_params['vec'].length.return_value = 5000.0
        mock_params['vec_normalized'].x.return_value = 0.0
        mock_params['vec_normalized'].y.return_value = 1.0
        
        mock_prepare_params.return_value = mock_params
        
        mock_layer = MagicMock()
        mock_generate_shp.return_value = mock_layer
        
        # Act
        self.racetrack_module.compute_way_points()
        
        # Assert
        mock_prepare_params.assert_called_once()
        mock_generate_shp.assert_called_once()
        mock_save_points.assert_called_once()
        points = mock_save_points.call_args[0][0]
        self.assertTrue(len(points) > 0, "Should have generated waypoints")

    @patch("ScienceFlightPlanner.racetrack_module.RacetrackModule._get_layer_parameters")
    def test_prepare_computation_parameters_no_layer(self, mock_get_layer):
        # Arrange
        mock_get_layer.return_value = None
        
        # Act
        result = self.racetrack_module._prepare_computation_parameters()
        
        # Assert
        self.assertIsNone(result)
        mock_get_layer.assert_called_once()

    @patch("ScienceFlightPlanner.racetrack_module.QgsVectorFileWriter.writeAsVectorFormat")
    @patch("ScienceFlightPlanner.racetrack_module.QgsVectorLayer")
    @patch("ScienceFlightPlanner.racetrack_module.RacetrackModule._get_save_file_path")
    def test_generate_points_shp_file(self, mock_get_save_path, mock_vector_layer, mock_write_vector):
        # Arrange
        mock_get_save_path.return_value = "/tmp/test_output.shp"
        mock_write_vector.return_value = (0, "")  # NoError
        
        mock_layer_instance = MagicMock()
        mock_layer_instance.isValid.return_value = True
        mock_vector_layer.return_value = mock_layer_instance
        
        self.racetrack_module.iface.addVectorLayer.return_value = mock_layer_instance
        
        flight_params = FlightParameters(
            flight_altitude=100.0,
            overlap=0.25,
            coverage_range=500.0,
            sensor_name="TestSensor",
            max_turn_distance=1000.0,
            algorithm=FIRST_ALGO_NAME
        )
        
        mock_crs = MagicMock()
        mock_crs.authid.return_value = "EPSG:4326"
        
        # Act
        with patch('os.path.exists', return_value=False):
            result = self.racetrack_module.generate_points_shp_file(
                "/tmp/input.shp", flight_params, mock_crs
            )
        
        # Assert
        self.assertIsNotNone(result)
        mock_get_save_path.assert_called_once()
        mock_vector_layer.assert_called()
        mock_write_vector.assert_called_once()
        self.racetrack_module.iface.addVectorLayer.assert_called_once()


def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRacetracks))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)