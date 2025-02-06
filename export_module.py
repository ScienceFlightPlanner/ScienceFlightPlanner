import os

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsWkbTypes
)
from qgis.gui import QgisInterface

import tempfile

from .constants import QGIS_FIELD_NAME_TAG, QGIS_FIELD_NAME_ID, DEFAULT_TAG
from .libs.garmin_fpl import wpt_to_gfp_20230704, DEC2DMM_20230704
from .utils import LayerUtils


TEMP_FILE_SUFFIX = "wp_DDM.wpt"

def wpt_to_gfp(input_file_path, output_file_path):
    with tempfile.NamedTemporaryFile(suffix=TEMP_FILE_SUFFIX, delete=False) as temp_file:
        DEC2DMM_20230704.dec2ddm(input_file_path, temp_file.name)
    try:
        wpt_to_gfp_20230704.convert_wpt_to_gfp(temp_file.name, output_file_path)
    finally:
        os.remove(temp_file.name)

def pad_with_zeros(number, expected_decimal_places):
    number_str = str(number)
    if "." not in number_str:
        return number_str + "." + str(0) * expected_decimal_places

    current_decimal_places = len(number_str.split(".")[1])
    return number_str + str(0) * (expected_decimal_places - current_decimal_places)

def shapefile_to_wpt(selected_layer, file_path):
    source_crs = selected_layer.crs()
    destination_crs = QgsCoordinateReferenceSystem("EPSG:4326")
    crs_translator = QgsCoordinateTransform(
        source_crs, destination_crs, QgsProject.instance()
    )

    with open(file_path, "w") as file:
        for f in selected_layer.getFeatures():
            id = "{:02d}".format(f.attribute(QGIS_FIELD_NAME_ID))
            comment = f.attribute(QGIS_FIELD_NAME_TAG)
            point = f.geometry().asPoint()
            transformed_point = crs_translator.transform(point)
            latitude = round(transformed_point.y(), 9)
            longitude = round(transformed_point.x(), 8)
            latitude_padded = pad_with_zeros(latitude, 9)
            longitude_padded = pad_with_zeros(longitude, 8)

            file.write(f"{id},{comment},{latitude_padded},{longitude_padded}\r\n")

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

        if selected_layer.fields().indexFromName(QGIS_FIELD_NAME_TAG) == -1:
            added = self.layer_utils.add_field_to_layer(
                selected_layer,
                QGIS_FIELD_NAME_TAG,
                QVariant.String,
                DEFAULT_TAG,
                "If 'tag' is not added, \nthe wpt file cannot be generated."
            )
            if not added:
                return

        shapefile_path = selected_layer.dataProvider().dataSourceUri().split('|')[0]

        wpt_file_path = self.get_file_path(shapefile_path, "Garmin Waypoint File (*.wpt)", "_user")
        gfp_file_path = self.get_file_path(shapefile_path, "Garmin Flightplan (*.gfp)", "_gfp")

        if not wpt_file_path.endswith(TEMP_FILE_SUFFIX) or gfp_file_path is not None:
            shapefile_to_wpt(selected_layer, wpt_file_path)

        if gfp_file_path is None:
            return

        wpt_to_gfp(wpt_file_path, gfp_file_path)

    def get_file_path(self, shapefile_path, filter, suggested_path_suffix):
        dialog_title = "Save Waypoints As"
        file_type = filter[-5:-1]
        file_path = self.layer_utils.create_file_dialog(dialog_title, shapefile_path, filter, suggested_path_suffix)

        if not file_path or file_path == "":
            if file_type == ".wpt":
                temp_file = tempfile.NamedTemporaryFile(suffix=TEMP_FILE_SUFFIX, delete=False)
                temp_file.close()
                file_path = temp_file.name
            elif file_type == ".gfp":
                return

        file_path = self.layer_utils.validate_file_path(file_path, file_type)

        return file_path