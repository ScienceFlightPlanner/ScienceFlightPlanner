import os
import sys

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsVectorLayer
from qgis.testing import unittest
from parameterized import parameterized
from unittest.mock import patch

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.export_module import shapefile_to_wpt, wpt_to_gfp, pad_with_zeros
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.utils import load_project, select_layer, tearDown_if_test_passed
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.BaseTest import BaseTest


class TestExport(BaseTest):
    plugin_instance: ScienceFlightPlanner

    def setUp(self):
        super().setUp()
        self.waypoint_tag_module = self.plugin_instance.waypoint_tag_module
        load_project()

    def compare_wpt_files(self, file1, file2):
        self.assertTrue(os.path.exists(file1), f"File path {file1} does not exist.")

        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        self.assertEqual(len(lines1), len(lines2), "The files have a different number of coordinates.")

        for i, (line1, line2) in enumerate(zip(lines1, lines2), start=1):
            self.assertEqual(line1, line2, f"Files differ at line {i}.")

        tearDown_if_test_passed(file1)

    def compare_gfp_files(self, file1, file2):
        self.assertTrue(os.path.exists(file1), f"File path {file1} does not exist.")

        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            file1_str = f1.read()
            file2_str = f2.read()

        file1_coords = file1_str.split(":F:")
        file2_coords = file2_str.split(":F:")

        self.assertEqual(file1_coords[0], file2_coords[0], f"File beginning is different: {file1_coords[0]} != {file2_coords[0]}")

        file1_coords = file1_coords[1:-1]
        file2_coords = file2_coords[1:-1]

        self.assertEqual(len(file1_coords), len(file2_coords), "The files have a different number of coordinates.")

        for file1_coord, file2_coord in zip(file1_coords, file2_coords):
            self.assertEqual(file1_coord[0], file2_coord[0],
                             f"Coordinate direction differ in {file1_coord} and {file2_coord}: {file1_coord[0]} != {file2_coord[0]}")
            self.assertEqual(file1_coord[6], file2_coord[6],
                             f"Coordinate direction differ in {file1_coord} and {file2_coord}: {file1_coord[6]} != {file2_coord[6]}")

            file1_latitude = int(file1_coord[1:5])
            file2_latitude = int(file2_coord[1:5])
            file1_longitude = int(file1_coord[7:12])
            file2_longitude = int(file2_coord[7:12])
            self.assertAlmostEqual(file1_latitude, file2_latitude,
                             msg=f"Coordinates differ in {file1_coord} and {file2_coord}: {file1_latitude} != {file2_latitude}", delta=1)
            self.assertAlmostEqual(file1_longitude, file2_longitude,
                             msg=f"Coordinates differ in {file1_coord} and {file2_coord}: {file1_longitude} != {file2_longitude}", delta=1)

        tearDown_if_test_passed(file1)

    def assertListEqualUnsorted(self, list1, list2):
        list1_sorted = sorted(list1)
        list2_sorted = sorted(list2)
        self.assertListEqual(list1_sorted, list2_sorted, f"Directory shouldn't contain file: {set(list1_sorted) - set(list2_sorted)}")

    # begin tests
    @parameterized.expand([
        ["Flight1", "resources/Flight1/Flight1.geojson", "resources/Flight1/Flight1_user.wpt", "resources/Flight1/Flight1_user_reference.wpt"],
        ["Flight3", "resources/Flight3/Flight3.geojson", "resources/Flight3/Flight3_user.wpt", "resources/Flight3/Flight3_user_reference.wpt"],
        ["Flight4", "resources/Flight4/Flight4.geojson", "resources/Flight4/Flight4_user.wpt", "resources/Flight4/Flight4_user_reference.wpt"],
    ])
    def test_wpt(self, name, input_file, output_file, expected):
        layer = QgsVectorLayer(input_file, "ogr")

        self.assertTrue(layer.isValid(), f"Vector layer failed to load: {input_file}")
        shapefile_to_wpt(layer, output_file)
        self.compare_wpt_files(output_file, expected)


    @parameterized.expand([
        ["Flight1", "resources/Flight1/Flight1_user_reference.wpt", "resources/Flight1/Flight1.gfp", "resources/Flight1/Flight1_reference.gfp"],
        ["Flight3", "resources/Flight3/Flight3_user_reference.wpt", "resources/Flight3/Flight3.gfp", "resources/Flight3/Flight3_reference.gfp"],
        ["Flight4", "resources/Flight4/Flight4_user_reference.wpt", "resources/Flight4/Flight4.gfp", "resources/Flight4/Flight4_reference.gfp"],
    ])
    def test_gfp(self, name, input_file, output_file, expected):
        wpt_to_gfp(input_file, output_file)
        self.compare_gfp_files(output_file, expected)


    @parameterized.expand([
        ["Flight1", "Flight1_wp", "resources/Flight1", "resources/Flight1/Flight1_test_wpt_QFileDialog_closed.gfp", "resources/Flight1/Flight1_reference.gfp"],
        ["Flight3", "Flight3_wp", "resources/Flight3", "resources/Flight3/Flight3_test_wpt_QFileDialog_closed.gfp", "resources/Flight3/Flight3_reference.gfp"],
        ["Flight4", "Flight4_wp", "resources/Flight4", "resources/Flight4/Flight4_test_wpt_QFileDialog_closed.gfp", "resources/Flight4/Flight4_reference.gfp"],
    ])
    @patch("ScienceFlightPlanner.utils.LayerUtils.create_file_dialog")
    def test_wpt_QFileDialog_closed(self, name, layer, output_directory, output_file, expected, mock_create_file_dialog):
        def side_effect(_0, _1, filter, _2):
            if filter == "Garmin Waypoint File (*.wpt)":
                return ""
            elif filter == "Garmin Flightplan (*.gfp)":
                return output_file
            return None

        mock_create_file_dialog.side_effect = side_effect

        select_layer(layer)

        files_in_directory_before = os.listdir(output_directory) + [output_file.split("/")[-1]]

        self.plugin_instance.export_module.shapefile_to_wpt_and_gfp()

        files_in_directory_after = os.listdir(output_directory)

        self.compare_gfp_files(output_file, expected)

        self.assertListEqualUnsorted(files_in_directory_before, files_in_directory_after)


    @parameterized.expand([
        ["Flight1", "Flight1_wp", "resources/Flight1", "resources/Flight1/Flight1_test_gfp_QFileDialog_closed.wpt",
         "resources/Flight1/Flight1_user_reference.wpt"],
        ["Flight3", "Flight3_wp", "resources/Flight3", "resources/Flight3/Flight3_test_gfp_QFileDialog_closed.wpt",
         "resources/Flight3/Flight3_user_reference.wpt"],
        ["Flight4", "Flight4_wp", "resources/Flight4", "resources/Flight4/Flight4_test_gfp_QFileDialog_closed.wpt",
         "resources/Flight4/Flight4_user_reference.wpt"],
    ])
    @patch("ScienceFlightPlanner.utils.LayerUtils.create_file_dialog")
    def test_gfp_QFileDialog_closed(self, name, layer, output_directory, output_file, expected,
                                    mock_create_file_dialog):
        def side_effect(_0, _1, filter, _2):
            if filter == "Garmin Waypoint File (*.wpt)":
                return output_file
            elif filter == "Garmin Flightplan (*.gfp)":
                return ""
            return None

        mock_create_file_dialog.side_effect = side_effect

        select_layer(layer)

        files_in_directory_before = os.listdir(output_directory) + [output_file.split("/")[-1]]

        self.plugin_instance.export_module.shapefile_to_wpt_and_gfp()

        files_in_directory_after = os.listdir(output_directory)

        self.compare_wpt_files(output_file, expected)

        self.assertListEqualUnsorted(files_in_directory_before, files_in_directory_after)


    @parameterized.expand([
        ["Flight1", "Flight1_wp", "resources/Flight1"],
        ["Flight3", "Flight3_wp", "resources/Flight3"],
        ["Flight4", "Flight4_wp", "resources/Flight4"],
    ])
    @patch("ScienceFlightPlanner.utils.LayerUtils.create_file_dialog")
    def test_wpt_and_gfp_QFileDialog_closed(self, name, layer, output_directory, mock_create_file_dialog):
        def side_effect(_0, _1, filter, _2):
            if filter == "Garmin Waypoint File (*.wpt)":
                return ""
            elif filter == "Garmin Flightplan (*.gfp)":
                return ""
            return None

        mock_create_file_dialog.side_effect = side_effect

        select_layer(layer)

        files_in_directory_before = os.listdir(output_directory)

        self.plugin_instance.export_module.shapefile_to_wpt_and_gfp()

        files_in_directory_after = os.listdir(output_directory)

        self.assertListEqualUnsorted(files_in_directory_before, files_in_directory_after)


    @parameterized.expand([
        ("exact_decimal_places", 12.12345678, 8, "12.12345678"),
        ("additional_zeros", 12.34, 9, "12.340000000"),
        ("no_decimal_places", 12, 9, "12.000000000"),
        ("negative_number", -12.3, 8, "-12.30000000"),
        ("zero_input", 0, 9, "0.000000000"),
    ])
    def test_pad_with_zeros(self, name, number, expected_decimal_places, expected_result):
        self.assertEqual(pad_with_zeros(number, expected_decimal_places), expected_result)


    @parameterized.expand([
        ("correct_extension", "example.txt", ".txt", "example.txt"),
        ("missing_extension", "example", ".txt", "example.txt"),
        ("case_insensitive_extension", "example.TXT", ".txt", "example.TXT"),
        ("empty_file_name", "", ".txt", ".txt"),
    ])
    def test_validate_file_path(self, name, file_path, file_type, expected_result):
        self.assertEqual(self.plugin_instance.layer_utils.validate_file_path(file_path, file_type), expected_result)

    # TODO
    @parameterized.expand([
        ("", "Flight_no_tag_wp", "resources/Flight1_user.wpt"),
    ])
    @patch("PyQt5.QtWidgets.QMessageBox.question")
    def NOtest_export_layer_without_tag_field(self, name, layer, output_file, mock_question_box):
        mock_question_box.return_value = QMessageBox.Yes

        select_layer(layer)
        # self.assertRaises(KeyError, partial(shapefile_to_wpt, layer, output_file))
        self.plugin_instance.export_module.shapefile_to_wpt_and_gfp()



def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExport))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)
