from typing import List
import os

from PyQt5.QtWidgets import QFileDialog
from qgis.core import Qgis, QgsPointXY, QgsVectorLayer, QgsWkbTypes
from qgis.gui import QgisInterface

from .utils import LayerUtils

import geopandas as gpd


class ExportModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def shapefile_to_geojson(self):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )

        if selected_layer is None:
            return

        shapefile_path = selected_layer.dataProvider().dataSourceUri().split('|')[0]
        print(shapefile_path)
        print(selected_layer.dataProvider().dataSourceUri())
        print(selected_layer.dataProvider().dataSourceUri().split('|'))

        gdf = gpd.read_file(shapefile_path)
        path_as_array = selected_layer.dataProvider().dataSourceUri().split('/')
        shapefile_name = path_as_array[-1]
        output_file_path = shapefile_path.replace(shapefile_name, "tmp.geojson")
        gdf.to_file(output_file_path, driver='GeoJSON')

    def shapefile_to_wpt(self):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        shapefile_path = selected_layer.dataProvider().dataSourceUri().split('|')[0]

        file_dialog = QFileDialog()
        title = "Save Waypoint Layer As"
        suggested_path, _ = os.path.splitext(shapefile_path)
        suggested_path += "_user"
        filter = "Garmin Waypoint File (*.wpt)"
        file_path, _ = QFileDialog.getSaveFileName(
            file_dialog, title, suggested_path, filter
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".wpt"):
            file_path += ".wpt"

        if os.path.exists(file_path):
            self.iface.messageBar().pushMessage(
                "Please select a file path that does not already exist",
                level=Qgis.Warning,
                duration=4,
            )
            return

        with open(file_path, "w") as file:
            for f in selected_layer.getFeatures():
                id = f.attribute("id")
                comment = ""
                point = f.geometry().asPoint()
                print(f"{id},{comment},{point.x()},{point.y()}\n")
                file.write(f"{id},{comment},{point.x()},{point.y()}\n")