from PyQt5.QtCore import QVariant
from qgis._core import QgsWkbTypes, Qgis, QgsVectorLayer, QgsField, QgsProject, QgsFeature
from qgis._gui import QgisInterface
from .constants import (
    QGIS_FIELD_NAME_ID,
    QGIS_FIELD_NAME_TAG,
    DEFAULT_TAG
)
from .utils import LayerUtils

class CutFlowlineModule:
    qgis_field_name = "cut_flowline"

    def __init__(self, iface: QgisInterface) -> None:
        """
        Initialize the CutFlowline module.

        Args:
            iface (QgisInterface): QGIS interface instance
        """
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def create_cut_layer(self, cut_features, crs):
        """
        Creates a new layer with the cut features and sequential IDs starting from 1,
        and adds a 'tag' field set to "fly-over".

        Args:
            cut_features (list): List of features to include in the new layer
            crs (QgsCoordinateReferenceSystem): Coordinate reference system for the new layer
        """
        cut_layer = QgsVectorLayer(f"Point?crs={crs.authid()}", "CutPoints", "memory")
        provider = cut_layer.dataProvider()

        # Add fields: 'id' (Int), 'tag' (String)
        provider.addAttributes([
            QgsField(QGIS_FIELD_NAME_TAG, QVariant.String)
        ])
        cut_layer.updateFields()

        # Create new features with sequential IDs and tag = "fly-over"
        new_features = []
        for i, original_feature in enumerate(cut_features, start=1):
            new_feature = QgsFeature()
            new_feature.setGeometry(original_feature.geometry())
            # 'id' -> i; 'tag' -> "fly-over"
            new_feature.setAttributes([i, DEFAULT_TAG])
            new_features.append(new_feature)

        # Add new features to the layer
        provider.addFeatures(new_features)
        QgsProject.instance().addMapLayer(cut_layer)
        self.iface.messageBar().pushMessage(
            "Info",
            "Cut points created with sequential IDs and tag = 'fly-over'.",
            level=Qgis.Info
        )

    def select_points(self):
        """
        Select two points from the point layer.

        Returns:
            tuple: A tuple containing the two point IDs (smaller_id, larger_id),
                  or None if selection is invalid
        """
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        if selected_layer is None:
            return None

        features = list(selected_layer.getSelectedFeatures())

        if len(features) != 2:
            self.iface.messageBar().pushMessage(
                "Error",
                "Please select exactly two points.",
                level=Qgis.Warning
            )
            return None

        point1_id = features[0].id()
        point2_id = features[1].id()

        # Return IDs in order (smaller, larger)
        return (min(point1_id, point2_id), max(point1_id, point2_id))

    def cut_action(self):
        """Execute the cut action on the selected points."""
        selected_ids = self.select_points()
        if selected_ids is None:
            return

        min_id, max_id = selected_ids
        point_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )

        if point_layer is None:
            self.iface.messageBar().pushMessage(
                "Error",
                "Please select a valid point layer.",
                level=Qgis.Warning
            )
            return

        # Create a list of features within the ID range
        cut_features = []
        for feature in point_layer.getFeatures():
            point_id = feature.id()
            if min_id <= point_id <= max_id:
                cut_features.append(feature)

        if cut_features:
            self.create_cut_layer(cut_features, point_layer.crs())
        else:
            self.iface.messageBar().pushMessage(
                "Info",
                "No points found within the selected range.",
                level=Qgis.Info
            )
