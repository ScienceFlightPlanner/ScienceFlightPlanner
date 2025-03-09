from typing import List

from qgis.core import Qgis, QgsPointXY, QgsVectorLayer, QgsWkbTypes
from qgis.gui import QgisInterface

from .constants import DEFAULT_PUSH_MESSAGE_DURATION
from .utils import LayerUtils


class WaypointGenerationModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def generate_waypoints_shp_file_action(self):
        """Generates an SHP-file that contains all waypoints of the selected line"""

        # retrieve waypoints of selected layer
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.LineGeometry]
        )
        if selected_layer is None:
            return

        waypoints = self._get_waypoints_of_layer(selected_layer)

        if not waypoints:
            return

        current_layer_path = selected_layer.dataProvider().dataSourceUri()

        waypoint_ids = list(range(1, len(waypoints) + 1))
        # generate shp-file
        self.layer_utils.generate_shp_file(
            current_layer_path, "_wp", waypoints, waypoint_ids, selected_layer.crs()
        )

    def _get_waypoints_of_layer(
        self, selected_layer: QgsVectorLayer
    ) -> List[QgsPointXY]:
        """Retrieves the waypoints of a line, if no line is selected a warning is printed and an empty list is
        returned"""
        if selected_layer.geometryType() != QgsWkbTypes.GeometryType.LineGeometry:
            # the selected layer is not a line
            self.iface.messageBar().pushMessage(
                "Please select a vector layer of type line",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return []

        # Get selected feature if more than one exists
        features = list(selected_layer.getFeatures())

        if len(features) == 0:
            self.iface.messageBar().pushMessage(
                "There are no features in the currently selected layer",
                level=Qgis.Info,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return []

        feature = self.layer_utils.get_selected_feature_from_layer(selected_layer)

        if feature is None:
            return []

        geometry = feature.geometry()
        geometry_single_type = QgsWkbTypes.isSingleType(geometry.wkbType())
        # retrieve waypoints of line
        if geometry_single_type:
            return geometry.asPolyline()
        else:
            points = []
            for part in geometry.asMultiPolyline():
                points.extend(part)
            return points
