from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsWkbTypes, 
    Qgis, 
    QgsVectorLayer, 
    QgsField, 
    QgsProject, 
    QgsFeature, 
    QgsVectorFileWriter
)
from qgis.gui import QgisInterface
from .constants import (
    QGIS_FIELD_NAME_ID,
    QGIS_FIELD_NAME_TAG,
    DEFAULT_TAG
)
from .utils import LayerUtils
import os
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox


class CutFlowlineModule:

    def __init__(self, iface: QgisInterface) -> None:
        """
        Initialize the CutFlowline module.

        Args:
            iface (QgisInterface): QGIS interface instance
        """
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def create_cut_layer(self, cut_features, crs, point_layer):
        """
        Creates a new layer with the cut features and sequential IDs starting from 1,
        and adds a 'tag' field with values preserved from the original layer if available.

        Args:
            cut_features (list): List of features to include in the new layer
            crs (QgsCoordinateReferenceSystem): Coordinate reference system for the new layer
            point_layer (QgsVectorLayer): The original layer containing the features
        """
        # Check if source layer has tag field
        has_tag_field = False
        tag_field_idx = -1
        if point_layer.fields().lookupField(QGIS_FIELD_NAME_TAG) >= 0:
            has_tag_field = True
            tag_field_idx = point_layer.fields().lookupField(QGIS_FIELD_NAME_TAG)

        # First, create the memory layer
        cut_layer = QgsVectorLayer(f"Point?crs={crs.authid()}", "Cut_Points", "memory")
        provider = cut_layer.dataProvider()

        # Add fields
        provider.addAttributes([
            QgsField(QGIS_FIELD_NAME_ID, QVariant.Int),
            QgsField(QGIS_FIELD_NAME_TAG, QVariant.String)
        ])
        cut_layer.updateFields()

        # Create new features with sequential IDs and original tags if available
        new_features = []
        for i, original_feature in enumerate(cut_features, start=1):
            new_feature = QgsFeature()
            new_feature.setGeometry(original_feature.geometry())
            
            # Use original tag if available, otherwise use DEFAULT_TAG
            tag = DEFAULT_TAG
            if has_tag_field:
                original_tag = original_feature.attribute(tag_field_idx)
                if original_tag:
                    tag = original_tag
            
            new_feature.setAttributes([i, tag])
            new_features.append(new_feature)

        # Add new features to the layer
        provider.addFeatures(new_features)
        QgsProject.instance().addMapLayer(cut_layer)
        
        # Show message about created memory layer
        self.iface.messageBar().pushMessage(
            "Info",
            "Cut points created with sequential IDs and preserved tags.",
            level=Qgis.Info
        )
        
        # Ask user if they want to save to disk
        save_to_disk = QMessageBox.question(
            self.iface.mainWindow(),
            "Save Cut Points",
            "Do you want to save the cut points as a shapefile?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes
        
        if save_to_disk:
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self.iface.mainWindow(),
                "Save Cut Points As",
                "",
                "ESRI Shapefile (*.shp)"
            )
            
            if not file_path:
                # User canceled the save dialog
                return
                
            # Ensure file has .shp extension
            if not file_path.lower().endswith('.shp'):
                file_path += '.shp'
                
            # Save the memory layer to disk
            error = QgsVectorFileWriter.writeAsVectorFormat(
                cut_layer,  # Use the already created memory layer
                file_path,
                "UTF-8",
                crs,
                "ESRI Shapefile"
            )
            
            if error[0] != QgsVectorFileWriter.NoError:
                self.iface.messageBar().pushMessage(
                    "Error",
                    f"Error creating shapefile: {error[1]}",
                    level=Qgis.Critical
                )
                return
            
            # Remove the memory layer from the project
            QgsProject.instance().removeMapLayer(cut_layer.id())
            
            # Add the file-based layer to the project instead
            file_layer = self.iface.addVectorLayer(file_path, "Cut_Points", "ogr")
            
            if not file_layer or not file_layer.isValid():
                self.iface.messageBar().pushMessage(
                    "Warning",
                    f"File created at {os.path.basename(file_path)}, but could not be loaded as a layer.",
                    level=Qgis.Warning
                )
                return
                
            self.iface.messageBar().pushMessage(
                "Info",
                f"Cut points saved to {os.path.basename(file_path)} and loaded as file-based layer.",
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
        return min(point1_id, point2_id), max(point1_id, point2_id)

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
            self.create_cut_layer(cut_features, point_layer.crs(), point_layer)
        else:
            self.iface.messageBar().pushMessage(
                "Info",
                "No points found within the selected range.",
                level=Qgis.Info
            )
