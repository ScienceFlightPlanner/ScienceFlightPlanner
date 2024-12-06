import os

from .libs.garmin_fpl import wpt_to_gfp_20230704

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

    def shapefile_to_wpt_and_gfp(self):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        shapefile_path = selected_layer.dataProvider().dataSourceUri().split('|')[0]

        wpt_file_path = create_file_dialog(shapefile_path, "Garmin Waypoint File (*.wpt)", "_user")

        gfp_file_path = create_file_dialog(shapefile_path, "Garmin Flightplan (*.gfp)", "_gfp")

        self.shapefile_to_wpt(selected_layer, wpt_file_path)

        self.wpt_to_gfp(wpt_file_path, gfp_file_path)

    def shapefile_to_wpt(self, selected_layer, file_path):
        file_path = self.validate_file_path(file_path, ".wpt")
        if file_path is None:
            return

        with open(file_path, "w") as file:
            for f in selected_layer.getFeatures():
                id = f.attribute("id")
                comment = f.attribute("tag")
                point = f.geometry().asPoint()
                latitude = round(point.y(), 9)
                longitude = round(point.x(), 8)
                file.write(f"{id},{comment},{latitude},{longitude}\n")

    def wpt_to_gfp(self, input_file_path, output_file_path):
        output_file_path = self.validate_file_path(output_file_path, ".gfp")
        if output_file_path is None:
            return

        wpt_to_gfp_20230704.convert_wpt_to_gfp(input_file_path, output_file_path)


    def validate_file_path(self, file_path, file_type):
        if not file_path:
            return

        if not file_path.lower().endswith(file_type):
            file_path += file_type

        if os.path.exists(file_path):
            self.iface.messageBar().pushMessage(
                "Please select a file path that does not already exist",
                level=Qgis.Warning,
                duration=4,
            )
            return
        return file_path

def create_file_dialog(shapefile_path, filter, suggested_path_suffix):
    file_dialog = QFileDialog()
    title = "Save Waypoint Layer As"
    suggested_path, _ = os.path.splitext(shapefile_path)
    suggested_path += suggested_path_suffix
    file_path, _ = QFileDialog.getSaveFileName(
        file_dialog, title, suggested_path, filter
    )
    return file_path