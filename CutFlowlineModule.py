from PyQt5.QtCore import QVariant
from qgis._core import QgsWkbTypes, Qgis, QgsFeature, QgsGeometry, QgsVectorLayer, QgsField, QgsProject, QgsCoordinateReferenceSystem
from qgis._gui import QgisInterface
from .utils import LayerUtils


class CutFlowlineModule:
    qgis_field_name = "cut_flowline"

    begin = None
    end = None

    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def create_cut_layer(self, cut_features, point_layer, crs):
        """Creates a new layer with the cut features."""
        # Create a new Point layer with the same CRS as the original point layer
        cut_layer = QgsVectorLayer(f"Point?crs={crs}", "CutPoints", "memory")
        provider = cut_layer.dataProvider()

        # Add fields for attributes (you can adjust the fields here)
        provider.addAttributes([QgsField("id", QVariant.Int)])
        cut_layer.updateFields()

        # Add cut features to the layer
        provider.addFeatures(cut_features)
        QgsProject.instance().addMapLayer(cut_layer)

        self.iface.messageBar().pushMessage("Info", "Cut points created.", level=Qgis.Info)

    def select_points(self):
        """Select two points from the point layer."""
        selected_layer = self.layer_utils.get_valid_selected_layer([QgsWkbTypes.GeometryType.PointGeometry])
        if selected_layer is None:
            return None

        selected_features = selected_layer.getSelectedFeatures()

        features = []
        for feature in selected_features:
            features.append(feature)

        if len(features) != 2:
            self.iface.messageBar().pushMessage("Error", "Please select exactly two points.", level=Qgis.Warning)
            return None

        first_point_id = features[0]["id"]
        last_point_id = features[1]["id"]

        return first_point_id, last_point_id

    def cut_action(self):
        selected_ids = self.select_points()

        if selected_ids is None:
            return

        first_point_id, last_point_id = selected_ids

        point_layer = self.layer_utils.get_valid_selected_layer([QgsWkbTypes.GeometryType.PointGeometry])
        crs = point_layer.crs()

        if point_layer is None:
            self.iface.messageBar().pushMessage("Error", "Please select a valid point layer.", level=Qgis.Warning)
            return

        # Create a list of features to keep within the selected range of IDs
        cut_features = []

        for feature in point_layer.getFeatures():
            point_id = feature["id"]
            if first_point_id <= point_id <= last_point_id:
                cut_features.append(feature)  # Add the point to the cut list if it is within the range

        if cut_features:
            self.create_cut_layer(cut_features, point_layer, crs)  # Pass the point_layer to create the new layer with the same CRS
        else:
            self.iface.messageBar().pushMessage("Info", "No points found within the selected range.", level=Qgis.Info)

    def delete_points_outside_range(self, first_point_id, last_point_id, point_layer):
        """Deletes points outside the selected ID range."""
        point_layer.startEditing()
        for feature in point_layer.getFeatures():
            point_id = feature["id"]
            if not (first_point_id <= point_id <= last_point_id):
                point_layer.dataProvider().deleteFeature(feature.id())
