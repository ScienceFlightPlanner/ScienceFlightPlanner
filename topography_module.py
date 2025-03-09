import os.path

import numpy as np
from qgis.PyQt.QtGui import QColor

from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QSpinBox,
    QHBoxLayout,
    QLabel,
    QToolBar,
    QDialog,
    QPushButton
)
from osgeo import gdal
from qgis.PyQt.QtCore import Qt

from qgis.core import (
    QgsCoordinateTransform,
    QgsProject,
    QgsDistanceArea,
    QgsTask,
    QgsApplication,
    LayerFilters,
    Qgis,
    QgsGeometry
)
from qgis.gui import (
    QgisInterface,
    QgsMapLayerComboBox,
    QgsRubberBand
)

from .constants import (
    PLUGIN_NAME,
    ICON_DIRECTORY_PATH
)
from .libs.pyqtgraph import PlotItem

from .libs import pyqtgraph as pg

from .utils import LayerUtils

class RasterSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Raster Layer")
        self.setModal(True)
        self.resize(300, 100)

        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout(self)

        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(LayerFilters.LayerFilter.RasterLayer)
        v_layout.addWidget(self.layer_combo)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)  # Closes dialog with success
        self.ok_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)  # Closes dialog without selecting


        h_layout.addWidget(self.ok_button)
        h_layout.addWidget(self.cancel_button)
        v_layout.addLayout(h_layout)

    def get_selected_layer(self):
        """Returns the selected Raster Layer"""
        return self.layer_combo.currentLayer()

class CustomAxisTop(pg.AxisItem):
    def __init__(self, wp_data_x):
        super().__init__(orientation="top")
        self.data_x = wp_data_x
        major_ticks = []
        minor_ticks = [(x, str(i + 1)) for i, x in enumerate(wp_data_x)]
        ticks = [major_ticks, minor_ticks]
        super().setTicks(ticks)


def plot(
        task,
        max_climbing_rate_meters,
        flight_speed_kmh,
        data_x,
        data_y,
):
    danger_points = []
    for i in range(len(data_x) - 1):
        x_distance = data_x[i + 1] - data_x[i]
        max_height_gain = max_climbing_rate_meters / ((flight_speed_kmh * 1000 / 60) / x_distance)
        y_distance = data_y[i + 1] - data_y[i]
        if max_height_gain <= y_distance:
            danger_points.append(i)

    lines = []
    for i in danger_points:
        x_1 = data_x[i]
        x_2 = data_x[i + 1]
        y_1 = data_y[i]
        y_2 = data_y[i + 1]
        lines.append(([x_1, x_2], [y_1, y_2]))

    return danger_points, lines


class PlotDock(QDockWidget):
    def __init__(self,
                 iface,
                 data_x,
                 data_y,
                 wp_data_x,
                 max_climb_rate_spinbox,
                 points,
                 layer_crs
                 ):
        super().__init__("Topography", iface.mainWindow())

        self.iface = iface
        self.data_x = np.array(data_x)
        self.x_max = self.data_x.max()
        self.data_y = np.array(data_y)
        self.y_max = self.data_y.max()
        self.wp_data_x = wp_data_x
        self.v_lines = []
        self.danger_lines = []
        self.max_climb_rate_spinbox = max_climb_rate_spinbox
        self.points = points
        self.rubber_bands = []
        self.layer_crs = layer_crs
        self.graph = PlotItem()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(True, True, 0.5)
        self.graph = self.plot_widget.plot(self.data_x, self.data_y)

        #self.plot_widget.getViewBox().border = pg.mkPen(color=(0, 0, 0), width=1)

        x_axis_top = CustomAxisTop(wp_data_x)
        self.plot_widget.setAxisItems({'top': x_axis_top})

        plot_height = self.y_max + 100

        self.plot_widget.getViewBox().setLimits(xMin=-10000, yMin=0, yMax=plot_height)
        self.plot_widget.getViewBox().setRange(xRange=(0, self.x_max), yRange=(0, self.y_max))

        self.plot_widget.getAxis("left").setLabel("Height", "m")
        self.plot_widget.getAxis("top").setLabel("Waypoint ID")
        self.plot_widget.getAxis("bottom").setLabel("Distance", "m")
        self.plot_widget.getAxis("bottom").enableAutoSIPrefix(False)

        self.v_lines = []
        for x in self.wp_data_x:
            line_x = [x, x]
            line_y = [0, plot_height]  # Full height of the plot

            v_line = self.plot_widget.plot(line_x, line_y, pen=pg.mkPen(color=(255, 255, 0, 100), width=1))
            v_line.setVisible(False)
            self.v_lines.append(v_line)

        dock_widget = QWidget()
        v_layout = QVBoxLayout(dock_widget)
        h_layout = QHBoxLayout(dock_widget)

        v_layout.addWidget(self.plot_widget)

        self.check_box = QCheckBox("Show Waypoints")
        self.check_box.setParent(self)
        self.check_box.stateChanged.connect(lambda: self.toggle_line())
        h_layout.addWidget(self.check_box, 0, Qt.AlignLeft)

        self.plot_widget.plotItem.autoBtn.setImageFile(os.path.join(ICON_DIRECTORY_PATH, "icon_scale_up_or_down.png"))
        self.plot_widget.plotItem.autoBtn._width = 32
        self.plot_widget.plotItem.autoBtn.update()

        h_layout.addStretch()

        v_layout.addLayout(h_layout)

        dock_widget.setLayout(v_layout)

        self.setWidget(dock_widget)

        self.setFeatures(QDockWidget.DockWidgetClosable)

        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self)

        self.max_climb_rate_spinbox.editingFinished.connect(
            self.plot_task
        )

        # self.max_climb_rate_spinbox.valueChanged.connect(
        #     self.plot_task
        # )

    def plot_task(self):
        max_climbing_rate_feet = self.max_climb_rate_spinbox.value()
        max_climbing_rate_meters = max_climbing_rate_feet / 3.28
        flight_speed_kmh, _ = QgsProject.instance().readDoubleEntry(
            PLUGIN_NAME, "flight_speed", 200
        )

        for line in self.danger_lines:
            self.plot_widget.removeItem(line)

        # globals()['task'] is needed because QgsTask is weird when used within function scopes
        globals()['task'] = QgsTask.fromFunction(
            "plot",
            plot,
            on_finished=self.task_completed,
            max_climbing_rate_meters=max_climbing_rate_meters,
            flight_speed_kmh=flight_speed_kmh,
            data_x=self.data_x,
            data_y=self.data_y
        )

        QgsApplication.taskManager().addTask(globals()['task'])

    def task_completed(self, exception, result=None):
        if exception is not None:
            raise exception

        danger_points, lines = result
        for line_x, line_y in lines:
            line = self.plot_widget.plot(line_x, line_y, pen=pg.mkPen(color=(255, 0, 0), width=1))
            self.danger_lines.append(line)

        for rubber_band in self.rubber_bands:
            rubber_band.reset()

        map_canvas = self.iface.mapCanvas()
        for i in danger_points:
            point_tuple = [self.points[i], self.points[i + 1]]
            geom = QgsGeometry.fromPolylineXY(point_tuple)
            rubber_band = QgsRubberBand(map_canvas, Qgis.GeometryType.Line)  # False = LineString
            rubber_band.setColor(QColor(255, 0, 0, 150))  # Semi-transparent red
            rubber_band.setWidth(7)  # Line width

            rubber_band.setToGeometry(geom, self.layer_crs)
            self.rubber_bands.append(rubber_band)


    def toggle_line(self):
        """ Show/Hide the vertical line when the button is clicked """
        for v_line in self.v_lines:
            v_line.setVisible(not v_line.isVisible())

    def closeWidget(self):
        self.iface.removeDockWidget(self)
        for rubber_band in self.rubber_bands:
            rubber_band.reset()

        super().close()

    def closeEvent(self, event):
        for rubber_band in self.rubber_bands:
            rubber_band.reset()

class TopographyModule:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.layer_utils = LayerUtils(iface)
        self.plot_dock_widget = None
        self.max_climb_rate_widget = QWidget()
        self.max_climb_rate_spinbox = QSpinBox()

    def init_gui(self, toolbar: QToolBar):
        self.max_climb_rate_spinbox.setMaximum(2000)
        self.max_climb_rate_spinbox.setValue(800)
        self.max_climb_rate_spinbox.setSingleStep(10)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Maximum climb rate in feet/min"))
        layout.addWidget(self.max_climb_rate_spinbox)
        layout.setContentsMargins(20, 0, 5, 0)
        self.max_climb_rate_widget.setLayout(layout)
        toolbar.addWidget(self.max_climb_rate_widget)

    def tmp(self):
        self.close()

        vector_layer = self.iface.layerTreeView().currentLayer()
        if not vector_layer.isValid():
            print("Error: Could not load vector layer")
            exit()

        dialog = RasterSelectionDialog(self.iface.mainWindow())
        result = dialog.exec_()

        if result == QDialog.Accepted:
            raster_layer = dialog.get_selected_layer()
            if raster_layer is None:
                print("Error: No raster selected")
                return
        else:
            self.close()
            return

        vector_layer_crs = vector_layer.crs()
        raster_path = raster_layer.dataProvider().dataSourceUri().split('|')[0]
        raster_ds = gdal.Open(raster_path)
        gdal_raster = gdal.Open(raster_path)
        band_number = 1
        band = gdal_raster.GetRasterBand(band_number)
        gt = raster_ds.GetGeoTransform()
        transform_to_raster_crs = QgsCoordinateTransform(vector_layer_crs, raster_layer.crs(), QgsProject.instance())
        distance_area = QgsDistanceArea()
        distance_area.setEllipsoid('WGS84')
        distance_area.setSourceCrs(vector_layer_crs, QgsProject.instance().transformContext())

        data_x = []
        data_y = []
        wp_data_x = []

        points = []

        features = list(vector_layer.getFeatures())

        sample_interval = 100.0  # every 100 meters

        total_distance = 0

        for i in range(len(features) - 1):
            current_feature = features[i]
            next_feature = features[i + 1]
            current_feature_geom = current_feature.geometry()
            next_feature_geom = next_feature.geometry()
            current_point = current_feature_geom.asPoint()
            next_point = next_feature_geom.asPoint()

            distance = distance_area.measureLine(current_point, next_point)
            wp_data_x.append(total_distance)
            total_distance += distance

            line = distance_area.geodesicLine(current_point, next_point, sample_interval)
            points_every_kilometre = line[0][:-1:10]

            for point in points_every_kilometre:
                points.append(point)

        wp_data_x.append(total_distance)
        points.append(features[-1].geometry().asPoint())

        total_distance = 0
        transformed_points = [transform_to_raster_crs.transform(p) for p in points]

        for i in range(len(transformed_points) - 1):
            current_point = points[i]
            next_point = points[i + 1]
            distance = distance_area.measureLine(current_point, next_point)

            current_point = transformed_points[i]
            px, py = world_to_pixel(current_point.x(), current_point.y(), gt)

            raster_value = band.ReadAsArray(px, py, 1, 1)[0][0]

            data_x.append(total_distance)
            data_y.append(raster_value)

            total_distance += distance

        current_point = transformed_points[-1]
        px, py = world_to_pixel(current_point.x(), current_point.y(), gt)

        raster_value = band.ReadAsArray(px, py, 1, 1)[0][0]

        data_x.append(total_distance)
        data_y.append(raster_value)

        self.plot_dock_widget = PlotDock(
            self.iface,
            data_x,
            data_y,
            wp_data_x,
            self.max_climb_rate_spinbox,
            points,
            vector_layer.crs()
        )
        self.plot_dock_widget.plot_task()

    def close(self):
        if self.plot_dock_widget is not None:
            self.plot_dock_widget.closeWidget()


def world_to_pixel(x, y, gt):
    px = int((x - gt[0]) / gt[1])
    py = int((y - gt[3]) / gt[5])  # Negative y resolution
    return px, py