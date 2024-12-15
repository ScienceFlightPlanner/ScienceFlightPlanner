from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from qgis.core import Qgis, QgsWkbTypes, QgsField
from qgis.gui import QgisInterface

from .utils import LayerUtils

class WaypointTagModule:
    max_tag_length = 10

    qgis_field_name = "tag"

    tags = ["Fly-over",
            "Fly-by",
            "RH 180",
            "RH 270",
            "LH 180",
            "LH 270",
            "Custom tag"]

    default_tag = tags[0]

    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def tag(self, tag):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        if selected_layer is None:
            return

        if selected_layer.fields().indexFromName(self.qgis_field_name) == -1:
            self.add_tag_field_to_layer(selected_layer)

        selected_features = selected_layer.getSelectedFeatures()
        selected_layer.startEditing()
        selected_layer.beginEditCommand("Add Tag for Waypoints")
        for feature in selected_features:
            feature.setAttribute(self.qgis_field_name, tag)
            selected_layer.updateFeature(feature)

        selected_layer.removeSelection()
        selected_layer.endEditCommand() #"Add Tag for Waypoints"

    def new_tag(self, parent):
        text, _ = QInputDialog.getText(parent, "Custom tag", "Enter name for custom tag:")
        if len(text) > self.max_tag_length:
            self.iface.messageBar().pushMessage(
                "Tag must be less than 10 characters",
                level=Qgis.Warning,
                duration=4,
            )
            return
        self.tag(text)

    def add_tag_field_to_layer(self, layer):
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            f"Add Field {self.qgis_field_name} to Layer {layer.name()}?",
            f"Add Field '{self.qgis_field_name}' to Layer {layer.name()}?\n\n"
            f"If '{self.qgis_field_name}' is not added ,\nselected Points cannot be tagged.",
            QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.No:
            return

        new_field = QgsField(self.qgis_field_name, QVariant.String)
        added = layer.dataProvider().addAttributes([new_field])
        if added:
            layer.updateFields()

        attr_map = {}
        field_id = layer.fields().indexFromName(self.qgis_field_name)
        for feature in layer.getFeatures():
            attr_map[feature.id()] = {field_id: self.default_tag}

        layer.dataProvider().changeAttributeValues(attr_map)
        layer.updateFields()