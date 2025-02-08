import re

from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QMessageBox
from qgis.core import (
    Qgis,
    QgsField,
    QgsWkbTypes,
    QgsFeature,
    QgsGeometry,
    QgsFields,
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
    QgsProject
)
from qgis.gui import QgisInterface

from .constants import DEFAULT_PUSH_MESSAGE_DURATION
from .utils import LayerUtils

class CombineFlightplansModule:

    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    # noinspection DuplicatedCode
    def combine(self):
        vector_layers = [layer for layer in QgsProject.instance().mapLayers().values() if
                         isinstance(layer, QgsVectorLayer)]
        layers_with_selected_features = [layer for layer in vector_layers if layer.selectedFeatureCount() > 0]

        if len(layers_with_selected_features) != 2:
            self.iface.messageBar().pushMessage(
                "Please select exactly 2 coordinates in 2 different layers",
                level=Qgis.Info,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        layer1, layer2 = layers_with_selected_features

        waypoints1 = [feature.geometry().asPoint() for feature in layer1.getFeatures()]
        waypoints2 = [feature.geometry().asPoint() for feature in layer2.getFeatures()]

        selected_features1 = list(layer1.getSelectedFeatures())
        selected_features2 = list(layer2.getSelectedFeatures())

        if len(selected_features1) != 1 or len(selected_features2) != 1:
            self.iface.messageBar().pushMessage(
                "Please select exactly 2 coordinates in 2 different layers",
                level=Qgis.Info,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        merge_waypoint1_id = selected_features1[0].attribute("id")
        merge_waypoint2_id = selected_features2[0].attribute("id")

        reply = QMessageBox.question(
            self.iface.mainWindow(),
            f"Combine Flightplans?",
            f"Combine {layer1.name()} and {layer2.name()}\n"
            f"with selected points {merge_waypoint1_id} and {merge_waypoint2_id}?",
            QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.No:
            return

        layer1_path = layer1.dataProvider().dataSourceUri().split('|')[0]

        layer2_path = layer2.dataProvider().dataSourceUri().split('|')[0]

        layer2_flight_number_match = re.search(r"Flight\d+", layer2_path)

        layer2_flight_number = "x"

        if layer2_flight_number_match is not None:
            layer2_flight_number_index = layer2_flight_number_match.end() - 1
            layer2_flight_number = layer2_path[layer2_flight_number_index]

        path_suffix = "_" + layer2_flight_number + "_combined"

        file_path = self.layer_utils.get_shp_file_path("Save Merged Layer As", layer1_path, path_suffix)

        if not file_path:
            return

        merged_waypoints = []
        id1 = 1 - 1
        id2 = merge_waypoint2_id - 1

        while id1 < merge_waypoint1_id:
            merged_waypoints.append(waypoints1[id1])
            id1 += 1

        while id2 < len(waypoints2):
            merged_waypoints.append(waypoints2[id2])
            id2 += 1

        id2 %= len(waypoints2)

        while id2 < merge_waypoint2_id - 1:
            merged_waypoints.append(waypoints2[id2])
            id2 += 1

        while id1 < len(waypoints1):
            merged_waypoints.append(waypoints1[id1])
            id1 += 1

        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))

        #file_path = r"C:\Users\maxim\OneDrive\Desktop\Bachelorpraktikum\BP-AdvancedScienceFlightPlanner\SLOGIS2024-Flight1\Flight3_combined2.shp"
        #file_path = r"resources/Flight_combined.shp"

        writer = self.layer_utils.create_vector_file_write(
            file_path,
            fields,
            QgsWkbTypes.Point,
            QgsCoordinateReferenceSystem("EPSG:4326")
        )

        for i, merged_waypoint in enumerate(merged_waypoints):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(merged_waypoint))
            feature.setAttributes([i + 1])
            writer.addFeature(feature)

        layer = self.iface.addVectorLayer(file_path, "", "ogr")
        del writer
        layer.reload()