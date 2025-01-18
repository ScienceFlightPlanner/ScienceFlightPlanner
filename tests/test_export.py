import os
import sys
from functools import partial

from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.utils import plugins
from qgis.testing import unittest
from parameterized import parameterized
from unittest.mock import patch

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.export_module import shapefile_to_wpt, wpt_to_gfp, pad_with_zeros
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.test_tags import load_project, select_layer


class TestExport(unittest.TestCase):
    plugin_instance: ScienceFlightPlanner

    def setUp(self):
        self.plugin_instance = plugins["ScienceFlightPlanner"]
        self.waypoint_tag_module = self.plugin_instance.waypoint_tag_module
        load_project()

    def compare_wpt_files(self, file1, file2):
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        self.assertEqual(len(lines1), len(lines2), "The files have a different number of coordinates.")

        for i, (line1, line2) in enumerate(zip(lines1, lines2), start=1):
            self.assertEqual(line1, line2, f"Files differ at line {i}.")

    def compare_gfp_files(self, file1, file2):
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
        ["Flight1", "Flight1_wp", "resources/Flight1/Flight1_test_gfp_without_wpt.gfp", "resources/Flight1/Flight1_reference.gfp"],
        ["Flight3", "Flight3_wp", "resources/Flight3/Flight3_test_gfp_without_wpt.gfp", "resources/Flight3/Flight3_reference.gfp"],
        ["Flight4", "Flight4_wp", "resources/Flight4/Flight4_test_gfp_without_wpt.gfp", "resources/Flight4/Flight4_reference.gfp"],
    ])
    @patch("ScienceFlightPlanner.export_module.ExportModule.create_file_dialog")
    def test_gfp_without_wpt(self, name, layer, output_file, expected, mock_create_file_dialog):
        def side_effect(_0, filter, _1):
            if filter == "Garmin Waypoint File (*.wpt)":
                return ""
            elif filter == "Garmin Flightplan (*.gfp)":
                return output_file
            return None

        mock_create_file_dialog.side_effect = side_effect

        select_layer(layer)

        self.plugin_instance.export_module.shapefile_to_wpt_and_gfp()

        self.compare_gfp_files(output_file, expected)

    #TODO
    def test_export_layer_without_tag_field(self):
        layer = QgsVectorLayer("resources/Flight1.geojson", "ogr")
        self.assertRaises(KeyError, partial(shapefile_to_wpt, layer, "resources/Flight1_user.wpt"))


def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExport))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)
