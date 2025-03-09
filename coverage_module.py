import math
from typing import Dict, Union

from PyQt5.QtWidgets import QToolBar
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsMapLayer,
    QgsPoint,
    QgsPointXY,
    QgsProject,
    QgsRenderContext,
    QgsSettings,
    QgsUnitTypes,
    QgsVector,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import Qt, QVariant
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSpinBox,
    QWidget,
)

from .utils import LayerUtils
from .constants import (
    SENSOR_COMBOBOX_DEFAULT_VALUE,
    QGIS_FIELD_NAME_ID,
    PLUGIN_SENSOR_SETTINGS_PATH,
    PLUGIN_OVERLAP_SETTINGS_PATH,
    PLUGIN_OVERLAP_ROTATION_SETTINGS_PATH,
    PLUGIN_NAME,
    DEFAULT_PUSH_MESSAGE_DURATION
)


class CoverageModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    settings: QgsSettings
    flight_altitude_widget: QWidget
    flight_altitude_spinbox: QSpinBox
    sensor_combobox: QComboBox

    SPINBOX_LABEL: str = "Flight altitude (AGL) in m:"
    DEFAULT_FLIGHT_ALTITUDE: int = 2000
    FLIGHT_ALTITUDE_MAXIMUM: int = 9999

    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

        self.settings = QgsSettings()
        self.flight_altitude_widget = QWidget()
        self.flight_altitude_spinbox = QSpinBox()
        self.sensor_combobox = QComboBox(self.iface.mainWindow())

    def init_gui(self, toolbar: QToolBar):
        self.flight_altitude_spinbox.setMaximum(self.FLIGHT_ALTITUDE_MAXIMUM)
        self.flight_altitude_spinbox.setValue(self.DEFAULT_FLIGHT_ALTITUDE)
        self.flight_altitude_spinbox.setSingleStep(10)
        self.flight_altitude_spinbox.valueChanged.connect(
            self.flight_altitude_value_changed
        )
        self.flight_altitude_spinbox.valueChanged.connect(
            self.sensor_coverage_flight_altitude_changed
        )
        self.iface.layerTreeView().currentLayerChanged.connect(
            self.flight_altitude_layer_changed
        )

        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.SPINBOX_LABEL))
        layout.addWidget(self.flight_altitude_spinbox)
        layout.setContentsMargins(5, 0, 5, 0)
        self.flight_altitude_widget.setLayout(layout)
        toolbar.addWidget(self.flight_altitude_widget)

        self.sensor_combobox.currentTextChanged.connect(self.sensor_selection_changed)
        self.iface.layerTreeView().currentLayerChanged.connect(
            self.sensor_coverage_layer_changed
        )
        self.set_sensor_combobox_entries()
        toolbar.addWidget(self.sensor_combobox)

    def close(self):
        self.flight_altitude_spinbox.valueChanged.disconnect(
            self.flight_altitude_value_changed
        )
        self.flight_altitude_spinbox.valueChanged.disconnect(
            self.sensor_coverage_flight_altitude_changed
        )
        self.iface.layerTreeView().currentLayerChanged.disconnect(
            self.flight_altitude_layer_changed
        )
        self.sensor_combobox.currentTextChanged.disconnect(
            self.sensor_selection_changed
        )
        self.iface.layerTreeView().currentLayerChanged.disconnect(
            self.sensor_coverage_layer_changed
        )

    def flight_altitude_value_changed(self):
        """Saves the current flight altitude selected in the toolbar as layer variable"""
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [
                QgsWkbTypes.GeometryType.LineGeometry,
                QgsWkbTypes.GeometryType.PolygonGeometry,
            ],
            display_error_messages=False,
        )
        if not selected_layer:
            return

        if selected_layer.geometryType() == QgsWkbTypes.GeometryType.PolygonGeometry:
            context = QgsExpressionContext()
            context.appendScopes(
                QgsExpressionContextUtils.globalProjectLayerScopes(selected_layer)
            )
            path_layer_id = QgsExpression("@sfp_sensor_coverage_path").evaluate(context)

            try:
                selected_layer = QgsProject.instance().mapLayers()[path_layer_id]
            except:
                return

        QgsExpressionContextUtils.setLayerVariable(
            selected_layer, "sfp_flight_altitude", self.flight_altitude_spinbox.value()
        )

    def flight_altitude_layer_changed(self, layer: QgsMapLayer):
        """Changes the flight altitude in the toolbar to the stored value of the layer variable"""
        if (
            not layer
            or layer.type() != QgsMapLayer.VectorLayer
            or (
                layer.geometryType() != QgsWkbTypes.GeometryType.LineGeometry
                and layer.geometryType() != QgsWkbTypes.GeometryType.PolygonGeometry
            )
        ):
            return

        if layer.geometryType() == QgsWkbTypes.GeometryType.PolygonGeometry:
            context = QgsExpressionContext()
            context.appendScopes(
                QgsExpressionContextUtils.globalProjectLayerScopes(layer)
            )
            path_layer_id = QgsExpression("@sfp_sensor_coverage_path").evaluate(context)

            try:
                layer = QgsProject.instance().mapLayers()[path_layer_id]
            except:
                return

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
        flight_altitude = QgsExpression("@sfp_flight_altitude").evaluate(context)
        self.flight_altitude_spinbox.blockSignals(True)
        if not flight_altitude:
            self.flight_altitude_spinbox.setValue(self.DEFAULT_FLIGHT_ALTITUDE)
            self.flight_altitude_spinbox.blockSignals(False)
            return

        try:
            flight_altitude_number = int(flight_altitude)
            if (
                flight_altitude_number < 0
                or flight_altitude_number > self.FLIGHT_ALTITUDE_MAXIMUM
            ):
                self.flight_altitude_spinbox.setValue(self.DEFAULT_FLIGHT_ALTITUDE)
            else:
                self.flight_altitude_spinbox.setValue(flight_altitude_number)
        except ValueError:
            self.flight_altitude_spinbox.setValue(self.DEFAULT_FLIGHT_ALTITUDE)

        self.flight_altitude_spinbox.blockSignals(False)

    def set_sensor_combobox_entries(self):
        """Sets the entries in the comboBox for the sensors"""
        self.sensor_combobox.clear()
        self.sensor_combobox.addItem(SENSOR_COMBOBOX_DEFAULT_VALUE)
        try:
            sensor_names = list(
                self.settings.value(PLUGIN_SENSOR_SETTINGS_PATH, {}).keys()
            )
        except:
            self.iface.messageBar().pushMessage(
                "Couldn't read sensor options",
                level=Qgis.MessageLevel.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        self.sensor_combobox.addItems(sensor_names)

    def sensor_selection_changed(self):
        """Updates the sensor coverage layer after sensor selection changed"""
        current_sensor = self.sensor_combobox.currentText()
        if current_sensor == SENSOR_COMBOBOX_DEFAULT_VALUE or current_sensor == "":
            return

        selected_layer = self.layer_utils.get_valid_selected_layer(
            [
                QgsWkbTypes.GeometryType.LineGeometry,
                QgsWkbTypes.GeometryType.PolygonGeometry,
            ]
        )

        if (
            not selected_layer
            or selected_layer.geometryType() != QgsWkbTypes.GeometryType.LineGeometry
        ):
            return

        self.update_sensor_coverage(selected_layer)

    def sensor_coverage_layer_changed(self, layer: QgsMapLayer):
        """Updates the sensor selection after the selected layer changed"""
        self.sensor_combobox.setCurrentText(SENSOR_COMBOBOX_DEFAULT_VALUE)
        if (
            not layer
            or layer.type() != QgsMapLayer.VectorLayer
            or (
                layer.geometryType() != QgsWkbTypes.GeometryType.LineGeometry
                and layer.geometryType() != QgsWkbTypes.GeometryType.PolygonGeometry
            )
        ):
            self.sensor_combobox.setEnabled(False)
        else:
            self.sensor_combobox.setEnabled(True)

    def sensor_coverage_flight_altitude_changed(self):
        """Updates all sensor coverage layers of the currently selected layer"""
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [
                QgsWkbTypes.GeometryType.LineGeometry,
                QgsWkbTypes.GeometryType.PolygonGeometry,
            ],
            display_error_messages=False,
        )

        if not selected_layer:
            return

        if selected_layer.geometryType() == QgsWkbTypes.GeometryType.PolygonGeometry:
            context = QgsExpressionContext()
            context.appendScopes(
                QgsExpressionContextUtils.globalProjectLayerScopes(selected_layer)
            )
            path_layer_id = QgsExpression("@sfp_sensor_coverage_path").evaluate(context)

            try:
                selected_layer = QgsProject.instance().mapLayers()[path_layer_id]
            except:
                return

        coverage_layers_dictionary = self.get_coverage_layers_dict(selected_layer)
        try:
            for sensor in coverage_layers_dictionary:
                self.update_sensor_coverage(selected_layer, sensor)
        except:
            return

    def sensor_coverage_sensor_settings_changed(self):
        """Updates all sensor coverage layers"""
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            coverage_layers_dictionary = self.get_coverage_layers_dict(layer)
            if not coverage_layers_dictionary:
                continue
            try:
                for sensor in coverage_layers_dictionary:
                    self.update_sensor_coverage(layer, sensor)
            except:
                continue

    def update_sensor_coverage(
        self, selected_layer: QgsMapLayer, sensor: Union[str, None] = None
    ):
        """Updates the sensor coverage layer of the selected layer and the selected sensor"""
        # Get required data to compute sensor coverage
        flight_altitude = self.flight_altitude_spinbox.value()

        current_sensor = sensor or self.sensor_combobox.currentText()
        if current_sensor == SENSOR_COMBOBOX_DEFAULT_VALUE or current_sensor == "":
            return

        try:
            sensor_opening_angle = float(
                self.settings.value(PLUGIN_SENSOR_SETTINGS_PATH, {})[
                    current_sensor
                ]
            )
        except:
            # Return if the coverage layer was deleted when updating it
            if sensor:
                return

            self.iface.messageBar().pushMessage(
                f"Couldn't read sensor options for sensor {current_sensor}",
                level=Qgis.MessageLevel.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        coverage_crs = self.get_valid_coverage_crs()
        if coverage_crs is None:
            return

        # Compute sensor coverage
        sensor_coverage_in_meters = self.compute_sensor_coverage_in_meters(
            sensor_opening_angle, flight_altitude
        )
        if sensor_coverage_in_meters < 0:
            return
        unit_factor = QgsUnitTypes.fromUnitToUnitFactor(
            QgsUnitTypes.DistanceUnit.DistanceMeters,
            coverage_crs.mapUnits(),
        )
        sensor_coverage = sensor_coverage_in_meters * unit_factor

        coverage_layers_dictionary = self.get_coverage_layers_dict(selected_layer)
        try:
            coverage_layer = QgsProject.instance().mapLayers()[
                coverage_layers_dictionary[current_sensor]
            ]
            self.remove_all_features(coverage_layer)
        except:
            # Return if the coverage layer was deleted when updating it
            if sensor:
                return

            coverage_layer = self.generate_coverage_shp_file(
                selected_layer.dataProvider().dataSourceUri(),
                selected_layer.crs(),
                current_sensor,
            )

            if not coverage_layer:
                self.sensor_combobox.setCurrentText(SENSOR_COMBOBOX_DEFAULT_VALUE)
                return

            QgsExpressionContextUtils.setLayerVariable(
                coverage_layer,
                "sfp_sensor_coverage_path",
                selected_layer.id(),
            )

        coverage_layers_dictionary[current_sensor] = coverage_layer.id()
        self.add_coverage_features(
            coverage_layer,
            selected_layer,
            sensor_coverage,
            coverage_crs,
        )
        QgsExpressionContextUtils.setLayerVariable(
            selected_layer,
            "sfp_sensor_coverage_layers",
            f"{coverage_layers_dictionary}",
        )

    def compute_sensor_coverage_in_meters(
        self, sensor_opening_angle: float, flight_altitude: int
    ) -> float:
        """Computes the sensor coverage (distance from flight path in one direction) in meters based on the opening
        angle of the sensor in degree and the flight altitude in meters"""
        if sensor_opening_angle < 0 or sensor_opening_angle >= 180:
            self.iface.messageBar().pushMessage(
                "Sensor opening angle is not sensible",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return -1
        return math.tan(math.radians(sensor_opening_angle) / 2) * flight_altitude

    def get_coverage_layers_dict(self, layer: QgsMapLayer) -> Dict[str, str]:
        """Returns the dictionary that contains the sensors and corresponding coverage layers for a given layer"""
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
        coverage_layers = QgsExpression("@sfp_sensor_coverage_layers").evaluate(context)

        try:
            return eval(coverage_layers)
        except:
            return {}

    def generate_coverage_shp_file(
        self,
        current_layer_path: str,
        crs: QgsCoordinateReferenceSystem,
        sensor_name: str,
    ) -> Union[QgsVectorLayer, None]:
        """Generates an SHP-File for the sensor coverage"""
        path_suffix = f"_coverage_{sensor_name}.shp"
        writer_layer_tuple = self.generate_shp_file(
            current_layer_path,
            path_suffix,
            QgsWkbTypes.Polygon,
            crs
        )
        if writer_layer_tuple is None:
            return

        writer, layer = writer_layer_tuple

        render_context = QgsRenderContext.fromMapSettings(
            self.iface.mapCanvas().mapSettings()
        )
        symbol_layer = layer.renderer().symbols(render_context)[0].symbolLayers()[0]
        symbol_layer.setBrushStyle(Qt.CrossPattern)
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())

        del writer
        return layer

    def remove_all_features(self, layer: QgsMapLayer):
        """Deletes all features of a layer"""
        feature_ids = []
        for feature in layer.getFeatures():
            feature_ids.append(feature.id())

        layer.dataProvider().deleteFeatures(feature_ids)

    def add_coverage_features(
        self,
        coverage_layer: QgsMapLayer,
        line_layer: QgsMapLayer,
        sensor_coverage: float,
        coverage_crs: QgsCoordinateReferenceSystem,
    ):
        """Adds the features to the coverage layer"""
        coverage_features = []
        for index, line_feature in enumerate(line_layer.getFeatures()):
            coverage_feature = QgsFeature(index)
            coverage_feature.setGeometry(
                self.compute_coverage_polygon(
                    line_feature.geometry(),
                    sensor_coverage,
                    line_layer.crs(),
                    coverage_crs,
                )
            )
            coverage_features.append(coverage_feature)

        coverage_layer.dataProvider().addFeatures(coverage_features)
        coverage_layer.reload()

    def compute_coverage_polygon(
        self,
        line_geometry: QgsGeometry,
        sensor_coverage: float,
        line_crs: QgsCoordinateReferenceSystem,
        coverage_crs: QgsCoordinateReferenceSystem,
    ) -> QgsGeometry:
        """Computes the coverage polygon for a given line"""
        if QgsWkbTypes.isSingleType(line_geometry.wkbType()):
            points_on_line = line_geometry.asPolyline()
        else:
            points_on_line = []
            for part in line_geometry.asMultiPolyline():
                points_on_line.extend(part)

        # Convert points to CRS selected for coverage computation
        transform_to_coverage_crs = QgsCoordinateTransform(
            line_crs, coverage_crs, QgsProject.instance()
        )
        transform_from_coverage_crs = QgsCoordinateTransform(
            coverage_crs, line_crs, QgsProject.instance()
        )

        for index in range(len(points_on_line)):
            points_on_line[index] = transform_to_coverage_crs.transform(
                points_on_line[index]
            )

        geometries = []

        for index in range(len(points_on_line) - 1):
            from_point = points_on_line[index]
            to_point = points_on_line[index + 1]
            vector = QgsVector(
                to_point.x() - from_point.x(), to_point.y() - from_point.y()
            )

            coverage_points_for_line_segment = []

            clockwise_vector = self.perpendicular_clockwise(vector, sensor_coverage)
            coverage_points_for_line_segment.append(
                QgsPointXY(
                    from_point.x() + clockwise_vector.x(),
                    from_point.y() + clockwise_vector.y(),
                )
            )
            coverage_points_for_line_segment.append(
                QgsPointXY(
                    to_point.x() + clockwise_vector.x(),
                    to_point.y() + clockwise_vector.y(),
                )
            )

            counter_clockwise_vector = self.perpendicular_counter_clockwise(
                vector, sensor_coverage
            )
            coverage_points_for_line_segment.append(
                QgsPointXY(
                    to_point.x() + counter_clockwise_vector.x(),
                    to_point.y() + counter_clockwise_vector.y(),
                )
            )
            coverage_points_for_line_segment.append(
                QgsPointXY(
                    from_point.x() + counter_clockwise_vector.x(),
                    from_point.y() + counter_clockwise_vector.y(),
                )
            )

            geometries.append(
                QgsGeometry.fromPolygonXY([coverage_points_for_line_segment])
            )

        unified_geometry = QgsGeometry.unaryUnion(geometries)
        unified_geometry.transform(transform_from_coverage_crs)

        return unified_geometry

    def perpendicular_clockwise(
        self, vector: QgsVector, sensor_coverage: float
    ) -> QgsVector:
        """Computes a vector perpendicular to the given vector (rotated clockwise) with the length of sensor_coverage"""
        if vector.x() == 0 and vector.y() == 0:
            normalized_perpendicular = QgsVector(0, 0)
        else:
            normalized_perpendicular = QgsVector(vector.y(), -vector.x()).normalized()
        return QgsVector(
            sensor_coverage * normalized_perpendicular.x(),
            sensor_coverage * normalized_perpendicular.y(),
        )

    def perpendicular_counter_clockwise(
        self, vector: QgsVector, sensor_coverage: float
    ) -> QgsVector:
        """Computes a vector perpendicular to the given vector (rotated counter-clockwise) with the length of
        sensor_coverage"""
        if vector.x() == 0 and vector.y() == 0:
            normalized_perpendicular = QgsVector(0, 0)
        else:
            normalized_perpendicular = QgsVector(-vector.y(), vector.x()).normalized()
        return QgsVector(
            sensor_coverage * normalized_perpendicular.x(),
            sensor_coverage * normalized_perpendicular.y(),
        )

    def generate_shp_file(
            self,
            current_layer_path: str,
            path_suffix: str,
            geometry_type: QgsWkbTypes,
            crs: QgsCoordinateReferenceSystem,
    ):
        dialog_title = "Save Waypoint Layer As"
        # select file path of shp-file
        file_path = self.layer_utils.get_shp_file_path(dialog_title, current_layer_path, path_suffix)

        if not file_path:
            return

        fields = QgsFields()
        fields.append(QgsField(QGIS_FIELD_NAME_ID, QVariant.Int))

        # create the File Writer
        writer = self.layer_utils.create_vector_file_write(
            file_path,
            fields,
            geometry_type,
            crs,
        )

        # add vector as layer
        layer = self.iface.addVectorLayer(file_path, "", "ogr")

        return writer, layer

    def generate_lines_shp_file(
        self,
        current_layer_path: str,
        flight_altitude: float,
        overlap: float,
        crs: QgsCoordinateReferenceSystem,
        sensor_name: str,
    ) -> Union[QgsVectorLayer, None]:
        """Generates an SHP-File for the sensor coverage lines"""
        path_suffix = f"_{sensor_name}_{flight_altitude}m_{overlap}overlap_coverage_lines.shp"
        writer_layer_tuple = self.generate_shp_file(
            current_layer_path,
            path_suffix,
            QgsWkbTypes.LineString,
            crs
        )
        if writer_layer_tuple is None:
            return

        writer, layer = writer_layer_tuple

        del writer
        return layer

    def compute_optimal_coverage_lines(self):
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
        if sensor == SENSOR_COMBOBOX_DEFAULT_VALUE:
            self.iface.messageBar().pushMessage(
                "No sensor selected",
                level=Qgis.MessageLevel.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        try:
            sensor_opening_angle = float(
                self.settings.value(PLUGIN_SENSOR_SETTINGS_PATH, {})[sensor]
            )
        except:
            # Return if the coverage layer was deleted when updating it
            if sensor:
                return

            self.iface.messageBar().pushMessage(
                f"Couldn't read sensor options for sensor {sensor}",
                level=Qgis.MessageLevel.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return
        crs = layer.crs()
        coverage_crs = self.get_valid_coverage_crs()
        if coverage_crs is None:
            return
        transform_to_coverage_crs = QgsCoordinateTransform(
            crs, coverage_crs, QgsProject.instance()
        )
        transform_from_coverage_crs = QgsCoordinateTransform(
            coverage_crs, crs, QgsProject.instance()
        )
        flight_altitude = self.flight_altitude_spinbox.value()
        coverage_range = self.compute_sensor_coverage_in_meters(
            sensor_opening_angle, flight_altitude
        )
        if coverage_range <= 0:
            return
        coverage_range = self.compute_sensor_coverage_in_meters(
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
            self.settings.value(PLUGIN_OVERLAP_SETTINGS_PATH, default_overlap)
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
        if int(self.settings.value(PLUGIN_OVERLAP_ROTATION_SETTINGS_PATH, 0)):
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
        line_layer = self.generate_lines_shp_file(
            layer.dataProvider().dataSourceUri(),
            flight_altitude,
            overlap,
            layer.crs(),
            sensor,
        )
        if line_layer is None:
            return
        i = 1
        while True:
            distance = 2 * coverage_range * overlap_factor * i - coverage_range
            if distance > vec.length() + coverage_range:
                break

            line_end = transform_from_coverage_crs.transform(
                QgsPointXY(
                    point_end.x() + vec_normalized.x() * distance,
                    point_end.y() + vec_normalized.y() * distance,
                )
            )

            line_start = transform_from_coverage_crs.transform(
                QgsPointXY(
                    point_start.x() + vec_normalized.x() * distance,
                    point_start.y() + vec_normalized.y() * distance,
                )
            )
            line = QgsGeometry.fromPolyline([QgsPoint(line_start), QgsPoint(line_end)])
            f = QgsFeature(i)
            f.setGeometry(line)
            line_layer.dataProvider().addFeature(f)
            i += 1
        line_layer.reload()
        QgsExpressionContextUtils.setLayerVariable(
            line_layer,
            "sfp_flight_altitude",
            flight_altitude,
        )
        self.flight_altitude_layer_changed(line_layer)

    def get_valid_coverage_crs(self):
        """Returns the coverage crs as set in the plugin settings. If no crs is set, an according warning is thrown."""
        coverage_crs = QgsCoordinateReferenceSystem(
            QgsProject.instance().readEntry(
                PLUGIN_NAME, "coverage_crs", None
            )[0]
        )
        if not coverage_crs.isValid():
            QMessageBox.information(
                self.iface.mainWindow(),
                "No CRS selected",
                'There is no CRS selected for computing the sensor coverage. \n\nPlease select the CRS you want to '
                'use via "Settings ▶ Options... ▶ ScienceFlightPlanner"',
                QMessageBox.Ok,
            )
            return
        return coverage_crs
