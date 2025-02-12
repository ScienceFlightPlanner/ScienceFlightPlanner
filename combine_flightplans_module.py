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

from .constants import (
    DEFAULT_PUSH_MESSAGE_DURATION,
    QGIS_FIELD_NAME_ID,
    QGIS_FIELD_NAME_TAG
)
from .utils import LayerUtils, layer_has_field

class CombineFlightplansModule:

    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def combine(self):
        vector_layers = [layer for layer in QgsProject.instance().mapLayers().values() if
                         isinstance(layer, QgsVectorLayer)]
        layers_with_selected_features = [layer for layer in vector_layers if layer.selectedFeatureCount() > 0]

        if len(layers_with_selected_features) != 2:
            self.iface.messageBar().pushMessage(
                "Please select exactly 2 coordinates in 2 different layers",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        layer1, layer2 = layers_with_selected_features

        layer1_has_id_field = layer_has_field(layer1, QGIS_FIELD_NAME_ID)
        layer2_has_id_field = layer_has_field(layer2, QGIS_FIELD_NAME_ID)

        if layer1.wkbType() != Qgis.WkbType.Point or layer2.wkbType() != Qgis.WkbType.Point:
            self.iface.messageBar().pushMessage(
                "Both layers must have geometry: point",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        if not layer1_has_id_field or not layer2_has_id_field:
            self.iface.messageBar().pushMessage(
                "One of the layers or both layers have no id field",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        features1 = [feature for feature in layer1.getFeatures()]
        features2 = [feature for feature in layer2.getFeatures()]

        selected_features1 = list(layer1.getSelectedFeatures())
        selected_features2 = list(layer2.getSelectedFeatures())

        if len(selected_features1) != 1 or len(selected_features2) != 1:
            self.iface.messageBar().pushMessage(
                "Please select exactly 2 coordinates in 2 different layers",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        merge_waypoint1_id = selected_features1[0].attribute("id")
        merge_waypoint2_id = selected_features2[0].attribute("id")

        if type(merge_waypoint1_id) is not int:
            self.iface.messageBar().pushMessage(
                f"id field of the selected feature in {layer1.name()} isn't an integer",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        if type(merge_waypoint2_id) is not int:
            self.iface.messageBar().pushMessage(
                f"id field of the selected feature in {layer2.name()} isn't an integer",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

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

        merged_features = (
                features1[:merge_waypoint1_id] +
                features2[merge_waypoint2_id:] +
                features2[:merge_waypoint2_id] +
                features1[merge_waypoint1_id:]
        )

        fields = QgsFields()
        id_field = QgsField(QGIS_FIELD_NAME_ID, QVariant.Int)
        tag_field = QgsField(QGIS_FIELD_NAME_TAG, QVariant.String)
        fields.append(id_field)
        fields.append(tag_field)

        writer = self.layer_utils.create_vector_file_write(
            file_path,
            fields,
            Qgis.WkbType.Point,
            QgsCoordinateReferenceSystem("EPSG:4326")
        )

        for i, merged_waypoint in enumerate(merged_features):
            feature = QgsFeature()
            feature.setGeometry(merged_waypoint.geometry())
            feature.setAttributes([i + 1, merged_waypoint.attribute(QGIS_FIELD_NAME_TAG)])
            writer.addFeature(feature)

        layer = self.iface.addVectorLayer(file_path, "", "ogr")
        del writer
        layer.reload()