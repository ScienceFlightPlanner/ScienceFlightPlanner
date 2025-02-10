import os
import sys

from PyQt5.QtWidgets import QMessageBox
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

TAG_LIST = TAGS + [CUSTOM_TAG]

class TestCombine(BaseTest):
    combine_flightplans_module: CombineFlightplansModule

    def setUp(self):
        super().setUp()
        self.combine_flightplans_module = self.plugin_instance.combine_flightplans_module

    @parameterized.expand([
        ["a", "Flight1", 10, "Flight3", 10, "Flight1_3_combined"],
        ["b", "Flight1", 1, "Flight3", 1, "Flight1_3_combined"],
        ["c", "Flight1", 10, "Flight3", 10, "Flight1_3_combined"],
    ])
    @patch("PyQt5.QtWidgets.QMessageBox.question")
    @patch("ScienceFlightPlanner.utils.LayerUtils.get_shp_file_path")
    def test_template(self, name, layer1_name, layer1_wp_id, layer2_name, layer2_wp_id, result_layer_name, mock_question_box, mock_get_shp_file_path):
        mock_get_shp_file_path.return_value = "/tests_directory/ScienceFlightPlanner/tests/"
        def side_effect(_0, path_of_current_layer, path_suffix):
            suggested_path, _ = os.path.splitext(path_of_current_layer)
            suggested_path += path_suffix
            file_path = self.plugin_instance.layer_utils.validate_file_path(suggested_path, ".shp")
            return file_path

        mock_question_box.side_effect = side_effect

        mock_get_shp_file_path.return_value = QMessageBox.Yes

        select_layer(layer1_name)
        select_features([layer1_wp_id])
        select_layer(layer2_name)
        select_features([layer2_wp_id])
        self.combine_flightplans_module.combine()

        layer1_name = get_layer(layer1_name)
        layer2_name = get_layer(layer2_name)
        combined_layer = get_layer(result_layer_name)

        num_of_tests_passed = 0
        with self.subTest("Correct layer name"):
            self.assertTrue(combined_layer is not None)
            num_of_tests_passed = increment_if_test_passed(num_of_tests_passed)

        with self.subTest("Correct number of features"):
            self.assertEqual(
                combined_layer.featureCount(),
                layer1_name.featureCount() + layer2_name.featureCount()
            )
            num_of_tests_passed = increment_if_test_passed(num_of_tests_passed)

        if num_of_tests_passed == 2:
            delete_layer(combined_layer)

def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCombine))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)