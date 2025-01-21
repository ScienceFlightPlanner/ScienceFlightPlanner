from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QInputDialog
from qgis.core import Qgis, QgsWkbTypes
from qgis.gui import QgisInterface

from .utils import LayerUtils

class WaypointTagModule:
    max_tag_length = 10

    qgis_field_name = "tag"

    tags = ["fly-over",
            "fly-by",
            "RH 180",
            "RH 270",
            "LH 180",
            "LH 270",
            "Custom tag"]

    default_tag = tags[0]

    message_box_text = f"If '{qgis_field_name}' is not added, \nselected Points cannot be tagged."

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
            added = self.layer_utils.add_field_to_layer(selected_layer, self.qgis_field_name, QVariant.String, self.default_tag, self.message_box_text)
            if not added:
                return

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