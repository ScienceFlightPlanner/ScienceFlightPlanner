import sys
import random

from qgis.utils import iface
from qgis.testing import unittest
from unittest.mock import patch

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.utils import install_package
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.constants import TAGS, CUSTOM_TAG
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.BaseTest import BaseTest
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.tests.utils import (
    load_project,
    deselect_selected_features,
    select_layer,
    tag_list_from_features,
    random_list,
    select_features
)
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.waypoint_tag_module import WaypointTagModule

TAG_LIST = TAGS + [CUSTOM_TAG]

class TestTags(BaseTest):
    waypoint_tag_module: WaypointTagModule

    def setUp(self):
        super().setUp()
        self.waypoint_tag_module = self.plugin_instance.waypoint_tag_module
        load_project()
        select_layer("SLOGIS2024-Flight1_wp")
        deselect_selected_features()

    def check_feature_changes(self, features_before, features_after, tag, ids):
        for i, (feature_before, feature_after) in enumerate(zip(features_before, features_after)):
            if i in ids:
                self.assertEqual(feature_after, tag, f"Wrong Tag in feature: {i + 1}")
            else:
                self.assertEqual(feature_after, feature_before, f"Wrong Tag in feature: {i + 1}")

    def test_add_tag_to_layer(self, tag = TAG_LIST[2], list_length = 12):
        features_before = tag_list_from_features(iface.layerTreeView().currentLayer().getFeatures())

        random_ids = random_list(list_length)
        select_features(random_ids)
        self.waypoint_tag_module.tag(tag)
        iface.layerTreeView().currentLayer().commitChanges()

        features_after = tag_list_from_features(iface.layerTreeView().currentLayer().getFeatures())

        self.check_feature_changes(features_before, features_after, tag, random_ids)

    @patch("qgis.PyQt.QtWidgets.QInputDialog.getText")
    def test_add_valid_custom_tag_to_layer(self, mock_get_text, tag = "CUSTOM TAG", list_length = 12):
        features_before = tag_list_from_features(iface.layerTreeView().currentLayer().getFeatures())

        random_ids = random_list(list_length)
        print(random_ids)
        select_features(random_ids)
        mock_get_text.return_value = (tag, True)
        self.waypoint_tag_module.new_tag(self.plugin_instance.popupMenu)
        iface.layerTreeView().currentLayer().commitChanges()

        features_after = tag_list_from_features(iface.layerTreeView().currentLayer().getFeatures())

        self.check_feature_changes(features_before, features_after, tag, random_ids)

    @patch("qgis.PyQt.QtWidgets.QInputDialog.getText")
    def test_add_invalid_custom_tag_to_layer(self, mock_get_text, tag = "too_long_tag_exceeding_10_characters", list_length = 12):
        features_before = tag_list_from_features(iface.layerTreeView().currentLayer().getFeatures())

        random_ids = random_list(list_length)
        select_features(random_ids)
        mock_get_text.return_value = (tag, True)
        self.waypoint_tag_module.new_tag(self.plugin_instance.popupMenu)
        iface.layerTreeView().currentLayer().commitChanges()

        features_after = tag_list_from_features(iface.layerTreeView().currentLayer().getFeatures())

        self.check_feature_changes(features_before, features_after, tag, [])

    def Notest_random(self):
        for i in range(5):
            tag = self.tags[random.randint(0, 5)]
            list_length = random.randint(0, 54)
            self.test_add_tag_to_layer(tag, list_length)

    def tearDown(self):
        deselect_selected_features()

def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTags))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)