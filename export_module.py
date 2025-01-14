import os

from PyQt5.QtWidgets import QFileDialog

from qgis.core import QgsWkbTypes
from qgis.gui import QgisInterface

import tempfile

from .libs.garmin_fpl import wpt_to_gfp_20230704, DEC2DMM_20230704
from .utils import LayerUtils


def validate_file_path(file_path, file_type):
    if not file_path:
        return

    if not file_path.lower().endswith(file_type):
        file_path += file_type

    return file_path


def wpt_to_gfp(input_file_path, output_file_path):
    output_file_path = validate_file_path(output_file_path, ".gfp")
    if output_file_path is None:
        return

    with tempfile.NamedTemporaryFile(suffix='wp_DDM.wpt', delete=False) as temp_file:
        print(temp_file.name)
        DEC2DMM_20230704.dec2ddm(input_file_path, temp_file.name)
    try:
        wpt_to_gfp_20230704.convert_wpt_to_gfp(temp_file.name, output_file_path)
    finally:
        os.remove(temp_file.name)

def pad_with_zeros(number, expected_decimal_places):
    current_decimal_places = len(str(number).split(".")[1])
    return str(number) + str(0) * (expected_decimal_places - current_decimal_places)

def shapefile_to_wpt(selected_layer, file_path):
    file_path = validate_file_path(file_path, ".wpt")
    if file_path is None:
        return

    with open(file_path, "w") as file:
        for f in selected_layer.getFeatures():
            id = f.attribute("id")
            comment = f.attribute("tag")
            point = f.geometry().asPoint()
            latitude = round(point.y(), 9)
            longitude = round(point.x(), 8)
            latitude_padded = pad_with_zeros(latitude, 9)
            longitude_padded = pad_with_zeros(longitude, 8)

            file.write(f"{id},{comment},{latitude_padded},{longitude_padded}\n")


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

        wpt_file_path = self.create_file_dialog(shapefile_path, "Garmin Waypoint File (*.wpt)", "_user")

        gfp_file_path = self.create_file_dialog(shapefile_path, "Garmin Flightplan (*.gfp)", "_gfp")

        shapefile_to_wpt(selected_layer, wpt_file_path)

        wpt_to_gfp(wpt_file_path, gfp_file_path)

    def create_file_dialog(self, shapefile_path, filter, suggested_path_suffix):
        file_dialog = QFileDialog(self.iface.mainWindow())
        title = "Save Waypoint Layer As"
        suggested_path, _ = os.path.splitext(shapefile_path)
        suggested_path += suggested_path_suffix
        file_path, _ = QFileDialog.getSaveFileName(
            file_dialog, title, suggested_path, filter
        )
        return file_path