import math
import os
from typing import Union, Tuple, List, Dict
from dataclasses import dataclass

from PyQt5.QtWidgets import (
    QSpinBox, QComboBox, QFileDialog, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from qgis._core import (
    QgsWkbTypes, Qgis,
    QgsGeometry, QgsVector, QgsPointXY,
    QgsFeature, QgsExpressionContextUtils,
    QgsVectorLayer,
    QgsFields, QgsField, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsUnitTypes,
)
from qgis.gui import QgisInterface
from PyQt5.QtCore import QVariant
from .coverage_module import CoverageModule
from .utils import LayerUtils


@dataclass
class FlightParameters:
    flight_altitude: float
    overlap: float
    coverage_range: float
    sensor_name: str
    max_turn_distance: float
    algorithm: str


class RacetrackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the dialog UI components"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._add_turning_distance_input()
        self._add_algorithm_selector()
        self._add_button_controls()

    def _add_turning_distance_input(self):
        """Add the turning distance input section"""
        dist_layout = QHBoxLayout()
        dist_label = QLabel("Maximum Turning Distance: ")
        self.dist_spinbox = QSpinBox()
        self.dist_spinbox.setRange(0, 10000)
        self.dist_spinbox.setValue(1000)
        dist_layout.addWidget(dist_label)
        dist_layout.addWidget(self.dist_spinbox)
        self.layout.addLayout(dist_layout)

    def _add_algorithm_selector(self):
        """Add the algorithm selection dropdown"""
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Algorithm:")
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["Fly to top and back", "Back and Forth"])
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        self.layout.addLayout(algo_layout)

    def _add_button_controls(self):
        """Add OK and Cancel buttons"""
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

    def get_values(self) -> Tuple[int, str]:
        return self.dist_spinbox.value(), self.algo_combo.currentText()


class RacetrackModule:
    def __init__(self, iface: QgisInterface, coverage_module: CoverageModule) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)
        self.coverage_module = coverage_module
        self._init_from_coverage_module()

    def _init_from_coverage_module(self):
        """Initialize attributes from coverage module"""
        self.settings = self.coverage_module.settings
        self.flight_altitude_widget = self.coverage_module.flight_altitude_widget
        self.flight_altitude_spinbox = self.coverage_module.flight_altitude_spinbox
        self.sensor_combobox = self.coverage_module.sensor_combobox

    def close(self):
        """Disconnect all signal handlers"""
        self._disconnect_signals()

    def _disconnect_signals(self):
        """Handle disconnection of all signal handlers"""
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

    def _get_layer_parameters(self) -> Union[Dict, None]:
        """Get layer, feature, and CRS parameters"""
        layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PolygonGeometry]
        )
        if layer is None:
            return None

        feature = self.layer_utils.get_selected_feature_from_layer(layer)
        if feature is None:
            return None

        coverage_crs = self.coverage_module.get_valid_coverage_crs()
        if coverage_crs is None:
            return None

        return {
            'layer': layer,
            'feature': feature,
            'crs': layer.crs(),
            'coverage_crs': coverage_crs
        }

    def _get_flight_parameters(self, layer: QgsVectorLayer) -> Union[FlightParameters, None]:
        """Get flight-related parameters including sensor settings"""
        sensor = self.sensor_combobox.currentText()

        if sensor == "No sensor":
            self.iface.messageBar().pushMessage(
                "No sensor selected",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )
            return None

        try:
            sensor_opening_angle = float(
                self.settings.value("science_flight_planner/sensors", {})[sensor]
            )
        except:
            if sensor:
                return None

            self.iface.messageBar().pushMessage(
                f"Couldn't read sensor options for sensor {sensor}",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )
            return None

        # Get user input from dialog
        dialog = RacetrackDialog(parent=self.iface.mainWindow())
        if dialog.exec_() == dialog.Accepted:
            max_turn_distance, algorithm = dialog.get_values()
        else:
            return None

        flight_altitude = self.flight_altitude_spinbox.value()
        coverage_range = self.coverage_module.compute_sensor_coverage_in_meters(
            sensor_opening_angle, flight_altitude
        )
        if coverage_range <= 0:
            return None

        default_overlap = 0
        overlap = float(
            self.settings.value("science_flight_planner/overlap", default_overlap)
        )

        return FlightParameters(
            flight_altitude=flight_altitude,
            overlap=overlap,
            coverage_range=coverage_range,
            sensor_name=sensor,
            max_turn_distance=max_turn_distance,
            algorithm=algorithm
        )

    def _prepare_geometry_parameters(self, feature: QgsFeature,
                                     crs: QgsCoordinateReferenceSystem,
                                     coverage_crs: QgsCoordinateReferenceSystem) -> Dict:
        """Prepare geometry-related parameters for computation"""
        transform_to_coverage_crs = QgsCoordinateTransform(
            crs, coverage_crs, QgsProject.instance()
        )
        transform_from_coverage_crs = QgsCoordinateTransform(
            coverage_crs, crs, QgsProject.instance()
        )

        # Transform geometry and get bounding box
        geometry = QgsGeometry(feature.geometry())
        geometry.transform(transform_to_coverage_crs)
        bounding_box = geometry.orientedMinimumBoundingBox()[0].asPolygon()

        # Extract corners
        bottom_right = bounding_box[0][0]
        top_right = bounding_box[0][1]
        top_left = bounding_box[0][2]
        bottom_left = bounding_box[0][3]

        # Compute vectors
        vertical_vec = QgsVector(
            bottom_left.x() - top_left.x(),
            bottom_left.y() - top_left.y()
        )
        horizontal_vec = QgsVector(
            bottom_left.x() - bottom_right.x(),
            bottom_left.y() - bottom_right.y()
        )

        # Determine flight direction
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

        unit_factor = QgsUnitTypes.fromUnitToUnitFactor(
            QgsUnitTypes.DistanceUnit.DistanceMeters,
            coverage_crs.mapUnits(),
        )

        return {
            'vec': vec,
            'vec_normalized': vec_normalized,
            'point_start': point_start,
            'point_end': point_end,
            'coverage_range': self.coverage_module.compute_sensor_coverage_in_meters(
                float(self.settings.value("science_flight_planner/sensors", {})[self.sensor_combobox.currentText()]),
                self.flight_altitude_spinbox.value()
            ) * unit_factor,
            'overlap_factor': 1 - float(self.settings.value("science_flight_planner/overlap", 0)),
            'max_turn_distance': float(self.settings.value("science_flight_planner/max_turn_distance", 1000))
        }

    def _handle_remaining_tracks(self, j: int, number_of_lines: int,
                                 max_flyover: int, inner_iteration: int,
                                 left_point: bool, params: dict) -> List[QgsPointXY]:
        """Handle the remaining tracks for back and forth algorithm"""
        points = []
        forward = True
        remaining_tracks = (
            number_of_lines - j if inner_iteration == 0
            else int((((2 * max_flyover) - inner_iteration) - 2) / 2)
        )

        for i in range(remaining_tracks):
            if forward:
                j = j + remaining_tracks
            else:
                j = j - remaining_tracks

            points.extend(self._compute_line_points(
                j, left_point, params['point_start'], params['point_end'],
                params['vec_normalized'], params['coverage_range'],
                params['overlap_factor']
            ))
            left_point = not left_point
            remaining_tracks = remaining_tracks - 1
            forward = not forward
            left_point = not left_point

        return points

    def _update_position(self, j: int, forward: bool, max_flyover: int,
                         line_from_bottom: int, number_of_lines: int) -> int:
        """Update position for fly to top algorithm"""
        if forward:
            if j + max_flyover > number_of_lines:
                if j + 1 <= number_of_lines:
                    return j + 1
                else:
                    return j + 1 - max_flyover
            else:
                return j + max_flyover
        else:
            if j == line_from_bottom:
                return j + 1
            elif j - max_flyover < line_from_bottom:
                return line_from_bottom
            else:
                return j - max_flyover

    def _get_save_file_path(self, base_path: str, sensor_name: str,
                            flight_altitude: float, overlap: float) -> str:
        """Get save file path for the waypoint layer"""
        suggested_file_path, _ = os.path.splitext(base_path)
        suggested_file_path += (
            f"_{sensor_name}_{flight_altitude}m_{overlap}overlap_coverage_lines.shp"
        )
        file_path, _ = QFileDialog.getSaveFileName(
            QFileDialog(), "Save Waypoint Layer As", suggested_file_path,
            "ESRI Shapefile (*.shp *.SHP)"
        )

        if file_path and not file_path.lower().endswith(".shp"):
            file_path += ".shp"

        return file_path

    def generate_points_shp_file(self, path_of_line: str, params: FlightParameters,
                                 crs: QgsCoordinateReferenceSystem) -> Union[QgsVectorLayer, None]:
        """Generates an SHP-File for the sensor coverage way points"""
        file_path = self._get_save_file_path(
            path_of_line, params.sensor_name, params.flight_altitude, params.overlap
        )

        if not file_path:
            return None

        if os.path.exists(file_path):
            self.iface.messageBar().pushMessage(
                "Please select a file path that does not already exist",
                level=Qgis.Warning, duration=4
            )
            return None

        return self._create_point_layer(file_path, crs)

    def _create_point_layer(self, file_path: str, crs: QgsCoordinateReferenceSystem) -> Union[QgsVectorLayer, None]:
        """Create and return a new point layer"""
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("tag", QVariant.String))

        writer = self.layer_utils.create_vector_file_write(
            file_path, fields, QgsWkbTypes.Point, crs
        )

        layer = self.iface.addVectorLayer(file_path, "", "ogr")
        del writer
        return layer

    def _compute_back_and_forth_points(self, params: dict) -> List[QgsPointXY]:
        """Compute waypoints for back and forth algorithm - exact original implementation"""
        points = []
        forward = True
        number_of_lines = math.ceil(params['vec'].length() / (params['coverage_range'] * 2))
        max_flyover = math.floor(params['max_turn_distance'] / params['coverage_range'] * 2)
        j = 1
        left_point = True
        reached_end = False
        inner_iteration = 0

        for k in range(number_of_lines):
            if not reached_end:
                dist = 2 * params['coverage_range'] * params['overlap_factor'] * j - params['coverage_range']
                start = QgsPointXY(
                    params['point_start'].x() + params['vec_normalized'].x() * dist,
                    params['point_start'].y() + params['vec_normalized'].y() * dist,
                )
                end = QgsPointXY(
                    params['point_end'].x() + params['vec_normalized'].x() * dist,
                    params['point_end'].y() + params['vec_normalized'].y() * dist
                )

                if left_point:
                    points.append(start)
                    points.append(end)
                else:
                    points.append(end)
                    points.append(start)

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

                for i in range(remaining_tracks):
                    if forward:
                        j = j + remaining_tracks
                    else:
                        j = j - remaining_tracks

                    dist = 2 * params['coverage_range'] * params['overlap_factor'] * j - params['coverage_range']
                    start = QgsPointXY(
                        params['point_start'].x() + params['vec_normalized'].x() * dist,
                        params['point_start'].y() + params['vec_normalized'].y() * dist,
                    )
                    end = QgsPointXY(
                        params['point_end'].x() + params['vec_normalized'].x() * dist,
                        params['point_end'].y() + params['vec_normalized'].y() * dist
                    )

                    if left_point:
                        points.append(start)
                        points.append(end)
                    else:
                        points.append(end)
                        points.append(start)

                    left_point = not left_point
                    remaining_tracks = remaining_tracks - 1
                    forward = not forward
                    left_point = not left_point
                break

        return points

    def _compute_fly_to_top_points(self, params: dict) -> List[QgsPointXY]:
        """Compute waypoints for fly to top and back algorithm - exact original implementation"""
        points = []
        left_point = True
        forward = True
        number_of_lines = math.ceil(params['vec'].length() / (params['coverage_range'] * 2))
        j = 1
        max_flyover = math.floor(params['max_turn_distance'] / params['coverage_range'] * 2)
        line_from_bottom = 2

        for k in range(number_of_lines):
            dist = 2 * params['coverage_range'] * params['overlap_factor'] * j - params['coverage_range']
            start = QgsPointXY(
                params['point_start'].x() + params['vec_normalized'].x() * dist,
                params['point_start'].y() + params['vec_normalized'].y() * dist,
            )
            end = QgsPointXY(
                params['point_end'].x() + params['vec_normalized'].x() * dist,
                params['point_end'].y() + params['vec_normalized'].y() * dist
            )

            if left_point:
                points.append(start)
                points.append(end)
            else:
                points.append(end)
                points.append(start)

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

        return points

    @staticmethod
    def _compute_line_points(j: int, left_point: bool, point_start: QgsPointXY,
                             point_end: QgsPointXY, vec_normalized: QgsVector,
                             coverage_range: float, overlap_factor: float) -> List[QgsPointXY]:
        """Compute start and end points for a single line"""
        dist = 2 * coverage_range * overlap_factor * j - coverage_range
        start = QgsPointXY(
            point_start.x() + vec_normalized.x() * dist,
            point_start.y() + vec_normalized.y() * dist,
        )
        end = QgsPointXY(
            point_end.x() + vec_normalized.x() * dist,
            point_end.y() + vec_normalized.y() * dist
        )
        return [start, end] if left_point else [end, start]

    def compute_way_points(self):
        """Main method to compute waypoints based on selected algorithm"""
        params = self._prepare_computation_parameters()
        if not params:
            return

        point_layer = self.generate_points_shp_file(
            params['layer'].dataProvider().dataSourceUri(),
            params['flight_params'],
            params['layer'].crs()  # Pass the CRS from the input layer
        )
        if not point_layer:
            return

        points = self._compute_points_for_algorithm(params)
        if not points:
            return

        self._save_points_to_layer(points, point_layer, params['flight_params'].flight_altitude)

    def _prepare_computation_parameters(self) -> Union[dict, None]:
        """Prepare all necessary parameters for waypoint computation"""
        layer_params = self._get_layer_parameters()
        if not layer_params:
            return None

        flight_params = self._get_flight_parameters(layer_params['layer'])
        if not flight_params:
            return None

        geometry_params = self._prepare_geometry_parameters(
            layer_params['feature'], layer_params['crs'],
            layer_params['coverage_crs']
        )

        return {**layer_params, **geometry_params, 'flight_params': flight_params}

    def _compute_points_for_algorithm(self, params: dict) -> List[QgsPointXY]:
        """Compute waypoints based on selected algorithm"""
        if params['flight_params'].algorithm == "Back and Forth":
            return self._compute_back_and_forth_points(params)
        elif params['flight_params'].algorithm == "Fly to top and back":
            return self._compute_fly_to_top_points(params)
        else:
            self.iface.messageBar().pushMessage(
                "This algorithm is not implemented",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )
            return []

    def _save_points_to_layer(self, points: List[QgsPointXY],
                              point_layer: QgsVectorLayer,
                              flight_altitude: float):
        """Save computed points to the vector layer"""
        provider = point_layer.dataProvider()

        features = []
        for i, point in enumerate(points):
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPointXY(point))
            f.setAttributes([int(i), "Fly-over"])
            features.append(f)

        provider.addFeatures(features)
        point_layer.reload()

        QgsExpressionContextUtils.setLayerVariable(
            point_layer,
            "sfp_flight_altitude",
            flight_altitude,
        )

        self.coverage_module.flight_altitude_layer_changed(point_layer)