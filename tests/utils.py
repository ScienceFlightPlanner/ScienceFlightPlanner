import os
import random
from typing import cast

random.seed(0)

from qgis.PyQt.QtWidgets import QToolBar, QToolButton
from qgis.core import (
    QgsProject,
    QgsProjectBadLayerHandler,
    QgsVectorLayer,
    QgsVectorFileWriter
)
from qgis.utils import iface

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner


class QgsProjectBadLayerDefaultHandler(QgsProjectBadLayerHandler):
    def handleBadLayers(self, layers):
        pass

def load_project():
    QgsProject.instance().setBadLayerHandler(QgsProjectBadLayerDefaultHandler())
    b = QgsProject.instance().read("resources/Test.qgz")
    if not b:
        raise Exception("Could not load QGIS project")

def get_layer(layer_name):
    return cast(QgsVectorLayer, QgsProject.instance().mapLayersByName(layer_name)[0])

def select_layer(layer_name):
    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    iface.layerTreeView().setCurrentLayer(layer)

def current_layer():
    return iface.layerTreeView().currentLayer()

def get_tag_actions():
    toolbar = iface.mainWindow().findChild(QToolBar, "ScienceFlightPlanner")
    tag_button = toolbar.findChildren(QToolButton)[5]
    tag_menu = tag_button.menu()
    return tag_menu.actions()

def select_features(ids):
    layer = current_layer()
    for id in ids:
        layer.select(id)

def deselect_selected_features():
    layer = current_layer()
    for f in layer.selectedFeatures():
        layer.deselect(f.id())

def random_list(l_size):
    return [random.randint(0, 53) for _ in range(l_size)]

def tag_list_from_features(features):
    tag_list = []
    for feature in features:
        tag_list.append(feature.attribute("tag"))
    return tag_list

def trigger_action(name):
    for action in get_tag_actions():
        if action.text() == name:
            action.trigger()

def increment_if_test_passed(i):
    return i+1

def tearDown_if_test_passed(output_file_path):
    os.remove(output_file_path)

def delete_layer(layer):
    shapefile_path = layer.dataProvider().dataSourceUri()
    QgsProject.instance().removeMapLayer(layer.id())
    QgsVectorFileWriter.deleteShapeFile(shapefile_path)
