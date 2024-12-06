from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QInputDialog
from qgis.core import Qgis, QgsWkbTypes, QgsField
from qgis.gui import QgisInterface

from .utils import LayerUtils

class WaypointTagModule:
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
            new_field = QgsField(self.qgis_field_name, QVariant.String)
            added = selected_layer.dataProvider().addAttributes([new_field])
            if added:
                selected_layer.updateFields()

            attr_map = {}
            field_id = selected_layer.fields().indexFromName(self.qgis_field_name)
            for feature in selected_layer.getFeatures():
                attr_map[feature.id()] = {field_id: self.default_tag}

            selected_layer.dataProvider().changeAttributeValues(attr_map)
            selected_layer.updateFields()

        selected_features = selected_layer.getSelectedFeatures()
        selected_layer.startEditing()
        selected_layer.beginEditCommand("Add Tag for Waypoints")
        for feature in selected_features:
            feature.setAttribute(self.qgis_field_name, tag)

        selected_layer.removeSelection()
        selected_layer.endEditCommand() #"Add Tag for Waypoints"

    def new_tag(self, parent):
        text, _ = QInputDialog.getText(parent, "Custom tag", "Enter name for custom tag:")
        if len(text) > 10:
            self.iface.messageBar().pushMessage(
                "Tag must be less than 10 characters",
                level=Qgis.Warning,
                duration=4,
            )
            return
        self.tag(text)