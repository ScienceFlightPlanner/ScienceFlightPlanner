import os

from PyQt5.QtWidgets import QFileDialog

from qgis.core import Qgis, QgsWkbTypes
from qgis.gui import QgisInterface

from .utils import LayerUtils


class ExportModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

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

        #source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        #destination_crs = QgsCoordinateReferenceSystem("EPSG:3413")
        #crs_translator = QgsCoordinateTransform(
        #    source_crs, destination_crs, QgsProject.instance()
        #)

        with open(file_path, "w") as file:
            for f in selected_layer.getFeatures():
                id = f.attribute("id")
                comment = f.attribute("tag")
                point = f.geometry().asPoint()
                latitude = round(point.y(), 9)
                longitude = round(point.x(), 8)
                print(f"{id},{comment},{latitude},{longitude}\n")
                file.write(f"{id},{comment},{latitude},{longitude}\n")

    def wpt_to_gfp(self):
        return
