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

    def shapefile_to_wpt_and_gfp(self):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        shapefile_path = selected_layer.dataProvider().dataSourceUri().split('|')[0]

        file_dialog = QFileDialog()
        title = "Save Waypoint Layer As"
        suggested_path, _ = os.path.splitext(shapefile_path)
        suggested_path += "_user"
        wpt_filter = "Garmin Waypoint File (*.wpt)"
        wpt_file_path, _ = QFileDialog.getSaveFileName(
            file_dialog, title, suggested_path, wpt_filter
        )

        file_dialog1 = QFileDialog()
        gfp_filter = "Garmin Flightplan (*.gfp)"
        gfp_file_path, _ = QFileDialog.getSaveFileName(
            file_dialog1, title, suggested_path, gfp_filter
        )

        self.shapefile_to_wpt(selected_layer, wpt_file_path)

        self.wpt_to_gfp(wpt_file_path, gfp_file_path)

        #source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        #destination_crs = QgsCoordinateReferenceSystem("EPSG:3413")
        #crs_translator = QgsCoordinateTransform(
        #    source_crs, destination_crs, QgsProject.instance()
        #)

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
                print(f"{id},{comment},{latitude},{longitude}\n")
                file.write(f"{id},{comment},{latitude},{longitude}\n")

    def wpt_to_gfp(self, input_file_path, output_file_path):
        """Create a flightplan from an ordered list of user waypoints.

            Parameters
            ----------
            input_file_path : str
                Path to the "*_user_renamed_DDM.wpt" file
            output_file_path : str
                New path under which the .gfp-file should be stored
                Recommendation: "{target}_fpl.gfp"
            """
        output_file_path = self.validate_file_path(output_file_path,".gfp")
        if output_file_path is None:
            return

        with open(input_file_path, 'r') as f:
            # Read lines from the input file
            lines = f.readlines()

        converted_lines = []
        for line in lines:
            parts = line.strip().split(',')
            # Remove dots, 'd', and 'm' characters from the coordinates and concatenate latitude and longitude
            coordinates = parts[2].replace('.', '').replace('d', '').replace('m', '') + parts[3].replace('.',
                                                                                                         '').replace(
                'd', '').replace('m', '')
            # Append the formatted coordinates to the converted lines
            converted_lines.append(f'{coordinates}')

        # Concatenate the converted lines with the :F: delimiter and the 'FPN/RI' starting info.
        output_content = 'FPN/RI:F:' + ':F:'.join(converted_lines)

        # write the .gfp-file to disk
        with open(output_file_path, 'w') as f:
            f.write(output_content)

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