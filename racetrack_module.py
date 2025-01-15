import math
import os
from typing import Dict, Union

from PyQt5.QtWidgets import (
    QWidget,
    QSpinBox,
    QComboBox,
    QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from qgis._core import (
    QgsWkbTypes,
    Qgis,
    QgsCoordinateTransform,
    QgsProject,
    QgsUnitTypes,
    QgsGeometry,
    QgsVector,
    QgsPointXY,
    QgsFeature,
    QgsPoint,
    QgsExpressionContextUtils,
    QgsSettings,
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
    QgsFields,
    QgsField,
    QgsVectorFileWriter,
)
from qgis.gui import QgisInterface
from PyQt5.QtCore import QVariant
from numba import farray

#from statsmodels.stats.libqsturng.make_tbls import q0100

from .coverage_module import CoverageModule
from .utils import LayerUtils

class RacetrackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Setting maximum turning distance
        dist_layout = QHBoxLayout()
        dist_label = QLabel("Maximum Turning Distance: ")
        self.dist_spinbox = QSpinBox()
        self.dist_spinbox.setRange(0, 10000) # How big could a turning circle be?
        self.dist_spinbox.setValue(1000)
        dist_layout.addWidget(dist_label)
        dist_layout.addWidget(self.dist_spinbox)
        self.layout.addLayout(dist_layout)

        # Setting an Algorithm
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Algorithm:")
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["Fly to top and back", "Back and Forth"])
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        self.layout.addLayout(algo_layout)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

    def get_values(self):
        return self.dist_spinbox.value(), self.algo_combo.currentText()



class RacetrackModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    settings: QgsSettings
    flight_altitude_widget: QWidget
    flight_altitude_spinbox: QSpinBox
    coverage_module: CoverageModule
    sensor_combobox: QComboBox

    def __init__(self, iface, coverage_module) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)
        self.coverage_module = coverage_module

        self.settings = self.coverage_module.settings
        self.flight_altitude_widget = self.coverage_module.flight_altitude_widget
        self.flight_altitude_spinbox = self.coverage_module.flight_altitude_spinbox
        self.sensor_combobox = self.coverage_module.sensor_combobox

    # disconnect not identified?
    def close(self):
        self.flight_altitude_spinbox.valueChanged.disconnect(
            self.coverage_module.flight_altitude_value_changed
        )
        self.flight_altitude_spinbox.valueChanged.disconnect(
            self.coverage_module.sensor_coverage_flight_altitude_changed
        )
        self.iface.layerTreeView().currentLayerChanged.disconnect(
            self.coverage_module.flight_altitude_layer_changed
        )
        self.sensor_combobox.currentTextChanged.disconnect(
            self.coverage_module.sensor_selection_changed
        )
        self.iface.layerTreeView().currentLayerChanged.disconnect(
            self.coverage_module.sensor_coverage_layer_changed
        )

    def generate_points_shp_file(
        self,
        path_of_line: str,
        flight_altitude: float,
        overlap: float,
        crs: QgsCoordinateReferenceSystem,
        sensor_name: str,
    ) -> Union[QgsVectorLayer, None]:
        """Generates an SHP-File for the sensor coverage way points"""
        # select file path of shp-file
        file_dialog = QFileDialog()
        title = "Save Waypoint Layer As"
        suggested_file_path, _ = os.path.splitext(path_of_line)
        #change name
        suggested_file_path += (
            f"_{sensor_name}_{flight_altitude}m_{overlap}overlap_coverage_lines.shp"
        )
        filter = "ESRI Shapefile (*.shp *.SHP)"
        file_path, _ = QFileDialog.getSaveFileName(
            file_dialog, title, suggested_file_path, filter
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".shp"):
            file_path += ".shp"

        if os.path.exists(file_path):
            self.iface.messageBar().pushMessage(
                "Please select a file path that does not already exist",
                level=Qgis.Warning,
                duration=4,
            )
            return

        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))

        # create the File Writer
        writer = self.layer_utils.create_vector_file_write(
            file_path,
            fields,
            QgsWkbTypes.Point,
            crs,
        )

        # add vector as layer
        layer = self.iface.addVectorLayer(file_path, "", "ogr")

        del writer
        return layer

    def compute_way_points(self):
        # load layer, feature, sensor, flight altitude and crs
        layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PolygonGeometry]
        )
        if layer is None:
            return

        feature = self.layer_utils.get_selected_feature_from_layer(layer)
        if feature is None:
            return

        sensor = self.sensor_combobox.currentText()

        if sensor == "No sensor":
            self.iface.messageBar().pushMessage(
                "No sensor selected",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )
            return

        try:
            sensor_opening_angle = float(
                self.settings.value("science_flight_planner/sensors", {})[sensor]
            )
        except:
            # Return if the coverage layer was deleted when updating it
            if sensor:
                return

            self.iface.messageBar().pushMessage(
                f"Couldn't read sensor options for sensor {sensor}",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )
            return

        crs = layer.crs()
        coverage_crs = self.coverage_module.get_valid_coverage_crs()
        if coverage_crs is None:
            return

        dialog = RacetrackDialog(parent=self.iface.mainWindow())
        if dialog.exec_() == dialog.Accepted:
            max_turn_distance, algorithm_choice = dialog.get_values()
        else:
            return


        transform_to_coverage_crs = QgsCoordinateTransform(
            crs, coverage_crs, QgsProject.instance()
        )
        transform_from_coverage_crs = QgsCoordinateTransform(
            coverage_crs, crs, QgsProject.instance()
        )
        flight_altitude = self.flight_altitude_spinbox.value()
        coverage_range = self.coverage_module.compute_sensor_coverage_in_meters(
            sensor_opening_angle, flight_altitude
        )
        if coverage_range <= 0:
            return
        coverage_range = self.coverage_module.compute_sensor_coverage_in_meters(
            sensor_opening_angle, flight_altitude
        )
        if coverage_range <= 0:
            return

        unit_factor = QgsUnitTypes.fromUnitToUnitFactor(
            QgsUnitTypes.DistanceUnit.DistanceMeters,
            coverage_crs.mapUnits(),
        )
        coverage_range *= unit_factor

        default_overlap = 0
        overlap = float(
            self.settings.value("science_flight_planner/overlap", default_overlap)
        )
        overlap_factor = 1 - overlap
        # create bounding box and extract its corners
        geometry = QgsGeometry(feature.geometry())
        geometry.transform(transform_to_coverage_crs)
        bounding_box = geometry.orientedMinimumBoundingBox()[0].asPolygon()
        bottom_right = bounding_box[0][0]
        top_right = bounding_box[0][1]
        top_left = bounding_box[0][2]
        bottom_left = bounding_box[0][3]

        # compute vector along which the flight lines are placed
        vertical_vec = QgsVector(
            bottom_left.x() - top_left.x(), bottom_left.y() - top_left.y()
        )
        horizontal_vec = QgsVector(
            bottom_left.x() - bottom_right.x(), bottom_left.y() - bottom_right.y()
        )
        draw_horizontal_lines = horizontal_vec.length() > vertical_vec.length()
        if int(self.settings.value("science_flight_planner/overlap_rotation", 0)):
            draw_horizontal_lines = not draw_horizontal_lines
        if draw_horizontal_lines:
            vec = vertical_vec
            vec_normalized = vec.normalized()
            point_start = top_left
            point_end = top_right
        else:
            vec = horizontal_vec
            vec_normalized = vec.normalized() * -1
            point_start = top_left
            point_end = bottom_left

        # generate lines and write to .shp file
        # create file
        # create waypoints

        point_layer = self.generate_points_shp_file(
            layer.dataProvider().dataSourceUri(),
            flight_altitude,
            overlap,
            layer.crs(),
            sensor,
        )
        if point_layer is None:
            return
        j = 1
        points = []
        max_fly_over_dist = max_turn_distance

        if algorithm_choice == "Back and Forth":
            forward = True
            number_of_lines = math.ceil(vec.length() / (coverage_range * 2))
            max_flyover = math.floor(max_turn_distance / coverage_range * 2)
            j = 1
            left_point = True
            reached_end = False
            inner_iteration = 0

            for k in range(number_of_lines):
                if not reached_end:
                    dist = 2 * coverage_range * overlap_factor * j - coverage_range
                    start, end = start_end_points(left_point, point_start, point_end, vec_normalized, dist)
                    points.append(start)
                    points.append(end)
                    left_point = not left_point
                    if forward:
                        if j + max_flyover <= number_of_lines:
                            j = j + max_flyover
                            inner_iteration = inner_iteration + 1
                            if ((j - 1) / ((2.0 * max_flyover) - 1.0)) % 1.0 != 0.0:
                                forward = not forward
                            else:
                                inner_iteration = 0
                        else:
                            reached_end = True
                    else:
                        j = (j - max_flyover) + 1
                        inner_iteration = inner_iteration + 1
                        forward = not forward
                else:
                    if inner_iteration == 0:
                        remaining_tracks = number_of_lines - j
                    else:
                        remaining_tracks = int((((2 * max_flyover) - inner_iteration) - 2) / 2)
                        self.iface.messageBar().pushMessage(
                            f"remaning tracks: {remaining_tracks}, max_flyover: {max_flyover}, inner_iteration: {inner_iteration} ",
                            level=Qgis.MessageLevel.Warning,
                            duration=20,
                        )
                    for i in range(remaining_tracks):
                        if forward:
                            j = j + remaining_tracks
                        else:
                            j = j - remaining_tracks

                        dist = 2 * coverage_range * overlap_factor * j - coverage_range
                        start, end = start_end_points(left_point, point_start, point_end, vec_normalized, dist)
                        points.append(start)
                        points.append(end)
                        left_point = not left_point
                        remaining_tracks = remaining_tracks - 1
                        forward = not forward
                        left_point = not left_point
                    break

        elif algorithm_choice == "Fly to top and back":
            left_point = True
            forward = True
            number_of_lines = math.ceil(vec.length()/(coverage_range * 2))
            j = 1
            max_flyover = math.floor(max_turn_distance / coverage_range * 2)
            # on_top = number_of_lines - 1 % max_flyover
            line_from_bottom = 2
            for k in range(number_of_lines):
                dist = 2 * coverage_range * overlap_factor * j - coverage_range
                start, end = start_end_points(left_point, point_start, point_end, vec_normalized, dist)
                points.append(start)
                points.append(end)
                left_point = not left_point
                if forward:
                    if j + max_flyover > number_of_lines:
                        if j + 1 <= number_of_lines:
                            j = j + 1
                            forward = not forward
                        else:
                            j = j + 1 - max_flyover
                            forward = not forward
                    else:
                        j = j + max_flyover
                else:
                    if j == line_from_bottom:
                        forward = not forward
                        j = j + 1
                        line_from_bottom += 2
                    elif j - max_flyover < line_from_bottom:
                        j = line_from_bottom
                        line_from_bottom += 1
                        forward = not forward
                    else:
                        j -= max_flyover
        else:
            self.iface.messageBar().pushMessage(
                f"This algorithm is not implemented",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )


        provider = point_layer.dataProvider()

        # Add fields: 'tag' as String
        provider.addAttributes([
            QgsField("tag", QVariant.String)  # new tag attribute
        ])
        layer.updateFields()

        for i, point in enumerate(points):
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(point))
            f.setAttributes([int(i), "Fly-over"])

            provider.addFeature(f)

        point_layer.reload()
        QgsExpressionContextUtils.setLayerVariable(
            point_layer,
            "sfp_flight_altitude",
            flight_altitude,
        )

        self.coverage_module.flight_altitude_layer_changed(point_layer)

def start_end_points(left_point, point_start, point_end, vec_normalized, dist):
    start = QgsPointXY(
        point_start.x() + vec_normalized.x() * dist,
        point_start.y() + vec_normalized.y() * dist,
    )
    end = QgsPointXY(
        point_end.x() + vec_normalized.x() * dist,
        point_end.y() + vec_normalized.y() * dist
    )
    if left_point:
        return start, end
    else:
        return end, start
