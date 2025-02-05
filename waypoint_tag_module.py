import re
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QInputDialog
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
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        if selected_layer is None:
            return

        if selected_layer.fields().indexFromName(QGIS_FIELD_NAME_TAG) == -1:
            added = self.layer_utils.add_field_to_layer(
                selected_layer,
                QGIS_FIELD_NAME_TAG,
                QVariant.String,
                DEFAULT_TAG,
                f"If '{QGIS_FIELD_NAME_TAG}' is not added, \nselected Points cannot be tagged."
            )
            if not added:
                return

        selected_features = selected_layer.getSelectedFeatures()
        selected_layer.startEditing()
        selected_layer.beginEditCommand("Add Tag for Waypoints")
        for feature in selected_features:
            feature.setAttribute(QGIS_FIELD_NAME_TAG, tag)
            selected_layer.updateFeature(feature)

        selected_layer.removeSelection()
        selected_layer.endEditCommand() #"Add Tag for Waypoints"

    def new_tag(self, parent):
        text, _ = QInputDialog.getText(parent, "Custom tag", "Enter name for custom tag:")
        if self.tag_is_valid(text):
            self.tag(text)

    def tag_is_valid(self, text):
        """
        Check if tag only consists of capital letters, spaces, or forward slash (/).
        https://atlaske-content.garmin.com/filestorage//email/outbound/attachments/GTN_Flight_Plan_and_User_Waypoint_transfer_Time1712844670119.pdf Section 3.2
        And also if it has 10 characters at most.
        """
        if len(text) > MAX_TAG_LENGTH:
            self.iface.messageBar().pushMessage(
                "Tag must be less than 10 characters",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return False

        pattern = r'^[A-Z0-9 /]$'
        if re.fullmatch(pattern, text) is None:
            self.iface.messageBar().pushMessage(
                "Tag may only consist of capital letters, spaces, or forward slash (/)",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return False

        return True
