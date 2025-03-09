from typing import List, Union

from qgis.core import QgsMapLayer, QgsProject, QgsWkbTypes
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QObject, QTimer

from .constants import (
    DISTANCE_ACTION_NAME,
    DURATION_ACTION_NAME,
    WAYPOINT_GENERATION_ACTION_NAME,
    COMBINE_FLIGHT_PLANS_ACTION_NAME,
    EXPORT_ACTION_NAME,
    TAG_ACTION_NAME,
    REDUCED_WAYPOINT_SELECTION_ACTION_NAME,
    REDUCED_WAYPOINT_GENERATION_ACTION_NAME,
    REVERSAL_ACTION_NAME,
    COVERAGE_LINES_ACTION_NAME,
    FLOWLINE_ACTION_NAME,
    CUT_FLOWLINE_ACTION_NAME,
    RACETRACK_ACTION_NAME,
    TOPOGRAPHY_ACTION_NAME,
    HELP_MANUAL_ACTION_NAME,
    FLIGHT_ALTITUDE_ACTION_NAME,
    SENSOR_COVERAGE_ACTION_NAME,
    MAX_CLIMB_RATE_ACTION_NAME
)


class ActionModule:
    iface: QgisInterface
    toolbar_items: Union[List[QObject], None]

    geometry_type_for_action = {
        DISTANCE_ACTION_NAME: [QgsWkbTypes.GeometryType.LineGeometry],
        DURATION_ACTION_NAME: [QgsWkbTypes.GeometryType.LineGeometry],
        WAYPOINT_GENERATION_ACTION_NAME: [QgsWkbTypes.GeometryType.LineGeometry],
        COMBINE_FLIGHT_PLANS_ACTION_NAME: [QgsWkbTypes.GeometryType.PointGeometry],
        EXPORT_ACTION_NAME: [QgsWkbTypes.GeometryType.PointGeometry],
        TAG_ACTION_NAME: [QgsWkbTypes.GeometryType.PointGeometry],
        REDUCED_WAYPOINT_SELECTION_ACTION_NAME: [QgsWkbTypes.GeometryType.PointGeometry],
        REDUCED_WAYPOINT_GENERATION_ACTION_NAME: [QgsWkbTypes.GeometryType.PointGeometry],
        REVERSAL_ACTION_NAME: [
            QgsWkbTypes.GeometryType.PointGeometry,
            QgsWkbTypes.GeometryType.LineGeometry,
        ],
        COVERAGE_LINES_ACTION_NAME: [QgsWkbTypes.GeometryType.PolygonGeometry],
        FLOWLINE_ACTION_NAME: [
            QgsWkbTypes.GeometryType.PointGeometry,
            QgsWkbTypes.GeometryType.LineGeometry,
        ],
        CUT_FLOWLINE_ACTION_NAME: [
            QgsWkbTypes.GeometryType.PointGeometry,
            QgsWkbTypes.GeometryType.LineGeometry,
        ],
        RACETRACK_ACTION_NAME: [
            QgsWkbTypes.GeometryType.PolygonGeometry,
        ],
        TOPOGRAPHY_ACTION_NAME: [QgsWkbTypes.GeometryType.PointGeometry],
        FLIGHT_ALTITUDE_ACTION_NAME: [
            QgsWkbTypes.GeometryType.LineGeometry,
            QgsWkbTypes.GeometryType.PolygonGeometry,
        ],
        SENSOR_COVERAGE_ACTION_NAME: [
            QgsWkbTypes.GeometryType.LineGeometry,
            QgsWkbTypes.GeometryType.PolygonGeometry,
        ],
        MAX_CLIMB_RATE_ACTION_NAME: [
            QgsWkbTypes.GeometryType.PointGeometry
        ]
    }

    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.current_layer = None
        self.proj = QgsProject.instance()
        self.message_box = None

    def connect(self, toolbar_items: List[QObject]):
        """connect the signal"""
        self.toolbar_items = list(
            filter(lambda action: action.toolTip() != HELP_MANUAL_ACTION_NAME, toolbar_items)
        )
        self.disable_invalid_actions_layer_wrapper()
        self.iface.layerTreeView().currentLayerChanged.connect(
            self.layer_selection_changed
        )

    def close(self):
        """disconnect the signal"""
        self.iface.layerTreeView().currentLayerChanged.disconnect(
            self.layer_selection_changed
        )

    def layer_selection_changed(self):
        """Call method when layer selection is changed"""
        QTimer().singleShot(0, self.disable_invalid_actions_layer_wrapper)

    def disable_invalid_actions_layer_wrapper(self):
        layers = self.iface.layerTreeView().selectedLayers()
        current_layer = self.iface.activeLayer()
        if len(layers) != 1 or current_layer != self.current_layer:
            self.current_layer = current_layer
            self.disable_invalid_actions_layer()

    def disable_invalid_actions_layer(self):
        """disables the buttons of the actions according to the current layer geometry"""
        layers = self.iface.layerTreeView().selectedLayers()
        if len(layers) != 1:
            self.current_layer = None
            to_disable = self.toolbar_items

        elif (
            self.current_layer is None
            or self.current_layer.type() != QgsMapLayer.VectorLayer
        ):
            to_disable = self.toolbar_items

        else:
            to_disable = []
            geometry_type = self.current_layer.geometryType()
            for action in self.toolbar_items:
                action.setDisabled(False)
                text = action.toolTip()
                if geometry_type not in self.geometry_type_for_action[text]:
                    to_disable.append(action)

        for action in to_disable:
            action.setDisabled(True)
