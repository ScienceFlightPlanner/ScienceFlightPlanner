import importlib
import sys
import os
import random

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.utils import install_package
from qgis.core import QgsProjectBadLayerHandler

try:
    importlib.import_module("pandas")
except ImportError:
    install_package("pandas")

try:
    importlib.import_module("numpy")
except ImportError:
    install_package("numpy")

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner

random.seed(0)

from PyQt5.QtWidgets import QToolBar, QToolButton
from qgis.core import QgsProject
from qgis.testing import unittest
from unittest.mock import patch

from qgis.utils import plugins

sys.path.insert(0, os.path.dirname(__file__))

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.waypoint_tag_module import WaypointTagModule
from qgis.utils import iface


class QgsProjectBadLayerDefaultHandler(QgsProjectBadLayerHandler):
    def handleBadLayers(self, layers):
        pass

def load_project():
    QgsProject.instance().setBadLayerHandler(QgsProjectBadLayerDefaultHandler())
    b = QgsProject.instance().read("resources/Test.qgz")
    if not b:
        raise Exception("Could not load QGIS project")

def select_layer():
    layer = QgsProject.instance().mapLayersByName("SLOGIS2024-Flight1_wp")[0]
    iface.layerTreeView().setCurrentLayer(layer)

def get_tag_actions():
    toolbar = iface.mainWindow().findChild(QToolBar, "ScienceFlightPlanner")
    tag_button = toolbar.findChildren(QToolButton)[5]
    tag_menu = tag_button.menu()
    return tag_menu.actions()

def select_features(ids):
    layer = iface.layerTreeView().currentLayer()
    for id in ids:
        layer.select(id)

def deselect_selected_features():
    layer = iface.layerTreeView().currentLayer()
    for f in layer.selectedFeatures():
        layer.deselect(f.id())

def random_list(l_size):
    return [random.randint(0, 53) for _ in range(l_size)]

def features_to_list(features):
    tag_list = []
    for feature in features:
        tag_list.append(feature.attribute("tag"))
    return tag_list

def trigger_action(name):
    for action in get_tag_actions():
        if action.text() == name:
            action.trigger()


class TestTags(unittest.TestCase):
    tags = ["Fly-over",
            "Fly-by",
            "RH 180",
            "RH 270",
            "LH 180",
            "LH 270",
            "Custom tag"]

    plugin_instance: ScienceFlightPlanner

    waypoint_tag_module: WaypointTagModule

    def setUp(self):
        self.plugin_instance = plugins["ScienceFlightPlanner"]
        self.waypoint_tag_module = self.plugin_instance.waypoint_tag_module
        load_project()
        select_layer()
        deselect_selected_features()

    def check_feature_changes(self, features_before, features_after, tag, ids):
        for i, (feature_before, feature_after) in enumerate(zip(features_before, features_after)):
            if i in ids:
                self.assertEqual(feature_after, tag)
            else:
                self.assertEqual(feature_after, feature_before)

    def test_add_tag_to_layer(self, tag = "RH 180", list_length = 12):
        features_before = features_to_list(iface.layerTreeView().currentLayer().getFeatures())

        random_ids = random_list(list_length)
        select_features(random_ids)
        self.waypoint_tag_module.tag(tag)
        iface.layerTreeView().currentLayer().commitChanges()

        features_after = features_to_list(iface.layerTreeView().currentLayer().getFeatures())

        self.check_feature_changes(features_before, features_after, tag, random_ids)

    @patch("PyQt5.QtWidgets.QInputDialog.getText")
    def test_add_valid_custom_tag_to_layer(self, mock_get_text, tag = "< 10 chars", list_length = 12):
        features_before = features_to_list(iface.layerTreeView().currentLayer().getFeatures())

        random_ids = random_list(list_length)
        select_features(random_ids)
        mock_get_text.return_value = (tag, True)
        self.waypoint_tag_module.new_tag(self.plugin_instance.popupMenu)
        iface.layerTreeView().currentLayer().commitChanges()

        features_after = features_to_list(iface.layerTreeView().currentLayer().getFeatures())

        self.check_feature_changes(features_before, features_after, tag, random_ids)

    @patch("PyQt5.QtWidgets.QInputDialog.getText")
    def test_add_invalid_custom_tag_to_layer(self, mock_get_text, tag = "too_long_tag_exceeding_10_characters", list_length = 12):
        features_before = features_to_list(iface.layerTreeView().currentLayer().getFeatures())

        random_ids = random_list(list_length)
        select_features(random_ids)
        mock_get_text.return_value = (tag, True)
        self.waypoint_tag_module.new_tag(self.plugin_instance.popupMenu)
        iface.layerTreeView().currentLayer().commitChanges()

        features_after = features_to_list(iface.layerTreeView().currentLayer().getFeatures())

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