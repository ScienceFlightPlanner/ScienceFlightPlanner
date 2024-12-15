from typing import List, Union

from qgis.core import QgsMapLayer, QgsProject, QgsWkbTypes
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QObject, QTimer


class ActionModule:
    iface: QgisInterface
    toolbar_items: Union[List[QObject], None]

    distance = "Display Flight Distance"
    duration = "Display Expected Flight Duration"
    waypoint_generation = "Generate Waypoints for Flightplan"
    export = "Export to Garmin"
    tag = "Add tag to selected waypoints"
    reduced_waypoint_selection = "Mark Selected Waypoints as Significant"
    reduced_waypoint_generation = (
        "Generate Reduced Flightplan from Significant Waypoints"
    )
    reversal = "Reverse Waypoints"
    coverage_lines = "Compute Optimal Coverage Lines"

    flowline = "Get flowline from file"
    cut_flowline = "Cut flowline to flightplan"
    racetrack = "Convert grid to racetrack"

    help_manual = "Help"

    flight_altitude = "Set Flight Altitude"
    sensor_coverage = "Select Sensor"

    geometry_type_for_action = {
        distance: [QgsWkbTypes.GeometryType.LineGeometry],
        duration: [QgsWkbTypes.GeometryType.LineGeometry],
        waypoint_generation: [QgsWkbTypes.GeometryType.LineGeometry],
        export: [QgsWkbTypes.GeometryType.PointGeometry],
        tag: [QgsWkbTypes.GeometryType.PointGeometry],
        reduced_waypoint_selection: [QgsWkbTypes.GeometryType.PointGeometry],
        reduced_waypoint_generation: [QgsWkbTypes.GeometryType.PointGeometry],
        reversal: [
            QgsWkbTypes.GeometryType.PointGeometry,
            QgsWkbTypes.GeometryType.LineGeometry,
        ],
        coverage_lines: [QgsWkbTypes.GeometryType.PolygonGeometry],
        flowline: [
            QgsWkbTypes.GeometryType.PointGeometry,
            QgsWkbTypes.GeometryType.LineGeometry,
        ],
        cut_flowline: [
            QgsWkbTypes.GeometryType.PointGeometry,
            QgsWkbTypes.GeometryType.LineGeometry,
        ],
        racetrack: [
            QgsWkbTypes.GeometryType.PolygonGeometry,
        ],
        flight_altitude: [
            QgsWkbTypes.GeometryType.LineGeometry,
            QgsWkbTypes.GeometryType.PolygonGeometry,
        ],
        sensor_coverage: [
            QgsWkbTypes.GeometryType.LineGeometry,
            QgsWkbTypes.GeometryType.PolygonGeometry,
        ],
    }

    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.current_layer = None
        self.proj = QgsProject.instance()
        self.message_box = None

    def connect(self, toolbar_items: List[QObject]):
        """connect the signal"""
        self.toolbar_items = list(
            filter(lambda action: action.toolTip() != self.help_manual, toolbar_items)
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
