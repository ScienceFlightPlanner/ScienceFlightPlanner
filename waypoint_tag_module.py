import re

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.core import Qgis, QgsWkbTypes
from qgis.gui import QgisInterface

from .utils import LayerUtils
from .constants import (
    MAX_TAG_LENGTH,
    QGIS_FIELD_NAME_TAG,
    DEFAULT_TAG,
    DEFAULT_PUSH_MESSAGE_DURATION
)


class WaypointTagModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def tag(self, tag):
        selected_layer = self.get_selected_layer_with_selected_features()

        if selected_layer is None:
            return

        self.add_tag_to_selected_features(selected_layer, tag)

    def new_tag(self, parent):
        selected_layer = self.get_selected_layer_with_selected_features()

        if selected_layer is None:
            return

        tag, _ = QInputDialog.getText(parent, "Custom tag", "Enter name for custom tag:")
        if self.tag_is_valid(tag):
            self.add_tag_to_selected_features(selected_layer, tag)

    def get_selected_layer_with_selected_features(self):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        if selected_layer is None:
            return

        if not self.at_least_one_feature_selected(selected_layer):
            return

        return selected_layer

    def add_tag_to_selected_features(self, layer, tag):
        if layer.fields().indexFromName(QGIS_FIELD_NAME_TAG) == -1:
            added = self.layer_utils.add_field_to_layer(
                layer,
                QGIS_FIELD_NAME_TAG,
                QVariant.String,
                DEFAULT_TAG,
                f"If '{QGIS_FIELD_NAME_TAG}' is not added, \nselected Points cannot be tagged."
            )
            if not added:
                return

        selected_features = layer.getSelectedFeatures()
        layer.startEditing()
        layer.beginEditCommand("Add Tag for Waypoints")
        for feature in selected_features:
            feature.setAttribute(QGIS_FIELD_NAME_TAG, tag)
            layer.updateFeature(feature)

        layer.removeSelection()
        layer.endEditCommand()  # "Add Tag for Waypoints"

    def at_least_one_feature_selected(self, layer):
        if layer.selectedFeatureCount() < 1:
            self.iface.messageBar().pushMessage(
                "Please select at least one waypoint",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return False

        return True

    def tag_is_valid(self, text):
        """
        Check if tag only consists of capital letters, spaces, or forward slash (/).
        https://atlaske-content.garmin.com/filestorage//email/outbound/attachments
        /GTN_Flight_Plan_and_User_Waypoint_transfer_Time1712844670119.pdf Section 3.2 And also if it has 10
        characters at most.
        """
        if len(text) > MAX_TAG_LENGTH:
            self.iface.messageBar().pushMessage(
                "Tag must be less than 10 characters",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return False

        pattern = fr'^[A-Z0-9 /]{{1,{MAX_TAG_LENGTH}}}$'  # = r'^[A-Z0-9 /]{1,<MAX_TAG_LENGTH>}$'
        if re.fullmatch(pattern, text) is None:
            self.iface.messageBar().pushMessage(
                "Tag may only consist of capital letters, spaces, or forward slash (/)",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return False

        return True
