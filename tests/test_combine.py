import os
import sys
import pandas

from PyQt5.QtWidgets import QMessageBox, QPushButton
from qgis._core import QgsProject
from qgis.testing import unittest
from parameterized import parameterized
from unittest.mock import patch

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.constants import (
    TAGS,
    CUSTOM_TAG,
    DEFAULT_TAG
)
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.BaseTest import BaseTest
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.utils import (
    get_layer,
    select_layer,
    select_features,
    current_layer,
    increment_if_test_passed,
    delete_layer
)
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.combine_flightplans_module import CombineFlightplansModule
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.constants import QGIS_FIELD_NAME_ID, QGIS_FIELD_NAME_TAG

TAG_LIST = TAGS + [CUSTOM_TAG]

class TestCombine(BaseTest):
    combine_flightplans_module: CombineFlightplansModule

    def setUp(self):
        super().setUp()
        self.combine_flightplans_module = self.plugin_instance.combine_flightplans_module

    @parameterized.expand([
        ["Concatenate_F1_F3", "Flight1", 21, "Flight3", 1, "Flight1", "Flight1_3_combined", "resources/Flight1_3_combined_wp21_1_reference.csv"],
        ["Concatenate_F3_F1", "Flight1", 1, "Flight3", 81, "Flight3", "Flight3_1_combined", "resources/Flight3_1_combined_wp81_1_reference.csv"],
        ["Combine_F1_F3_at_10_10", "Flight1", 10, "Flight3", 10, "Flight1", "Flight1_3_combined", "resources/Flight1_3_combined_wp10_10_reference.csv"],
        ["Combine_F3_F1_at_10_10", "Flight1", 10, "Flight3", 10, "Flight3", "Flight3_1_combined", "resources/Flight3_1_combined_wp10_10_reference.csv"],
    ])
    @patch("PyQt5.QtWidgets.QMessageBox.addButton")
    @patch("PyQt5.QtWidgets.QMessageBox.exec")
    @patch("PyQt5.QtWidgets.QMessageBox.clickedButton")
    @patch("ScienceFlightPlanner.utils.LayerUtils.get_shp_file_path")
    def test_combine(self, name, layer1, layer1_wp_id, layer2, layer2_wp_id, start_layer, result_layer_name, expected, mock_get_shp_file_path, mock_clicked_button, mock_exec, mock_add_button):
        def side_effect1(_0, path_of_current_layer, path_suffix):
            suggested_path, _ = os.path.splitext(path_of_current_layer)
            suggested_path += path_suffix
            file_path = self.plugin_instance.layer_utils.validate_file_path(suggested_path, ".shp")
            return file_path

        button1 = QPushButton
        button2 = QPushButton()

        def side_effect2(*args):
            if isinstance(args[0], str) and start_layer == layer2:
                button2.setText(args[0])
                return button2
            return button1

        def side_effect3():
            return button2

        mock_get_shp_file_path.side_effect = side_effect1

        mock_add_button.side_effect = side_effect2

        mock_clicked_button.side_effect = side_effect3

        mock_exec.return_value = None

        select_layer(layer1)
        select_features([layer1_wp_id - 1])
        select_layer(layer2)
        select_features([layer2_wp_id - 1])
        self.combine_flightplans_module.combine()

        layer1 = get_layer(layer1)
        layer2 = get_layer(layer2)
        combined_layer = get_layer(result_layer_name)

        num_of_tests_passed = 0
        with self.subTest("Correct layer name"):
            self.assertTrue(combined_layer is not None)
            num_of_tests_passed = increment_if_test_passed(num_of_tests_passed)

        with self.subTest("Correct number of features"):
            self.assertEqual(
                combined_layer.featureCount(),
                layer1.featureCount() + layer2.featureCount()
            )
            num_of_tests_passed = increment_if_test_passed(num_of_tests_passed)

        with self.subTest("Correct waypoint order"):
            csv = pandas.read_csv(expected)
            for i, feature in enumerate(combined_layer.getFeatures()):
                id = feature.attribute(QGIS_FIELD_NAME_ID)
                reference_id = i + 1
                self.assertEqual(id, reference_id)

                tag = feature.attribute(QGIS_FIELD_NAME_TAG)
                reference_tag = csv.at[i, "tag"]
                self.assertEqual(reference_tag, tag)

                latitude = feature.geometry().asPoint().y()
                reference_latitude = csv.at[i, "Y"]
                self.assertAlmostEqual(latitude, reference_latitude, delta = 0.0000000000001)

                longitude = feature.geometry().asPoint().x()
                reference_longitude = csv.at[i, "X"]
                self.assertAlmostEqual(longitude, reference_longitude, delta = 0.0000000000001)

            num_of_tests_passed = increment_if_test_passed(num_of_tests_passed)

        if num_of_tests_passed == 3:
            delete_layer(combined_layer)

def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCombine))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)