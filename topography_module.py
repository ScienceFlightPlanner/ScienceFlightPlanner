import math

import numpy as np
from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QCheckBox
from osgeo import gdal
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis._core import QgsUnitTypes, QgsExpressionContext, QgsExpressionContextUtils, QgsExpression, QgsGeometry, \
    QgsDistanceArea, QgsEllipsoidUtils, QgsCoordinateReferenceSystem, QgsCoordinateTransformContext
from qgis.core import QgsPointXY, QgsCoordinateTransform, QgsRasterLayer, QgsVectorLayer, QgsProject
from qgis.gui import QgisInterface

from .libs.pyqtgraph import Point
from .libs.pyqtgraph import debug
from .utils import install_package

from .libs import pyqtgraph as pg

#import pyqtgraph as pg

from .utils import LayerUtils

class CustomAxis(pg.AxisItem):

    def __init__(self, wp_data_x, plot_pixel_height):
        super().__init__(orientation="top", showValues=True)
        # Define custom labels (map numerical positions to strings)
        self.data_x = wp_data_x
        #super().setHeight(30)
        #super().setStyle(hideOverlappingLabels=True, tickLength = -plot_pixel_height)
        major_ticks = [(x, str(i + 1)) for i, x in enumerate(wp_data_x)]
        minor_ticks = []
        ticks = [major_ticks, minor_ticks]
        ticks = [minor_ticks, major_ticks]
        super().setTicks(ticks)

    def tickStringss(self, values, scale, spacing):
        """ Override to replace tick labels with custom text """
        strings = []
        for v in values:
            for x in self.data_x:
                if v == x:
                    strings.append(str(x))

        return strings


class PlotDock(QDockWidget):
    def __init__(self,
                 iface: QgisInterface,
                 data_x,
                 data_y,
                 wp_data_x,
                 danger_points
                 ):
        super().__init__("Topography", iface.mainWindow())

        # Create a QWidget for the dock
        dock_widget = QWidget()
        layout = QVBoxLayout(dock_widget)

        self.setWindowTitle("Linear Function Plot")
        #self.setGeometry(100, 100, 600, 400)

        # Create a PyQtGraph PlotWidget
        #self.plot_widget = pg.PlotWidget()
        x = np.array(data_x)  # replace None value by np.nan
        y = np.array(data_y)
        self.plot_widget = pg.plot(x, y)
        self.plot_widget.showGrid(True, True, 0.5)

        #self.plot_widget.getViewBox().autoRange()
        #self.plot_widget.getViewBox().disableAutoRange()
        self.plot_widget.getViewBox().border = pg.mkPen(color=(0, 0, 0), width=1)

        pixel_height = self.plot_widget.height()
        print("pixel_height", pixel_height)
        x_axis = CustomAxis(wp_data_x, pixel_height)
        self.plot_widget.setAxisItems({'top': x_axis})
        y_max = max(data_y)
        self.plot_widget.getViewBox().setLimits(xMin=-10000, yMin=0, yMax=y_max + 100)

        for i in danger_points:
            x_1 = data_x[i]
            x_2 = data_x[i + 1]
            y_1 = data_y[i]
            y_2 = data_y[i + 1]
            line_x = [x_1, x_2]
            line_y = [y_1, y_2]

            line = self.plot_widget.plot(line_x, line_y, pen=pg.mkPen(color=(255, 0, 0, 100), width=1))

        self.v_lines = []
        for x in wp_data_x:
            line_x = [x, x]
            line_y = [0, y_max + 100]  # Full height of the plot

            v_line = self.plot_widget.plot(line_x, line_y, pen=pg.mkPen(color=(0, 255, 0, 100), width=1))
            self.v_lines.append(v_line)
            v_line.setVisible(False)

        self.plot_widget.getAxis("left").setLabel("Height", "m")
        self.plot_widget.getAxis("top").setLabel("Waypoint ID")
        self.plot_widget.getAxis("bottom").setLabel("Distance", "m")

        layout.addWidget(self.plot_widget)

        self.check_box = QCheckBox("Show Waypoints")
        self.check_box.setParent(self)
        self.check_box.stateChanged.connect(lambda: self.toggle_line())
        layout.addWidget(self.check_box)

        dock_widget.setLayout(layout)

        self.setWidget(dock_widget)

        self.setFeatures(QDockWidget.DockWidgetClosable)

        iface.addDockWidget(Qt.BottomDockWidgetArea, self)

    def toggle_line(self):
        """ Show/Hide the vertical line when the button is clicked """
        for v_line in self.v_lines:
            v_line.setVisible(not v_line.isVisible())

class TopographyModule:

    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def tmp(self):
        raster_path = r"C:\Users\maxim\Downloads\DEM.tif"

        vector_layer = self.iface.layerTreeView().currentLayer()
        if not vector_layer.isValid():
            print("Error: Could not load vector layer")
            exit()

        # Load raster
        raster_layer = QgsRasterLayer(raster_path, "Raster Layer", "gdal")
        if not raster_layer.isValid():
            print("Error: Could not load raster layer")
            exit()

        raster_ds = gdal.Open(raster_path)
        gt = raster_ds.GetGeoTransform()
        transform_to_raster_crs = QgsCoordinateTransform(vector_layer.crs(), raster_layer.crs(), QgsProject.instance())
        band_number = 1  # Assuming single-band raster

        data_x = []
        data_y = []
        wp_data_x = []

        total_distance = 0

        points = []

        features = list(vector_layer.getFeatures())

        s = 0

        for i in range(len(features) - 1):
            current_feature = features[i]
            next_feature = features[i + 1]
            current_feature_geom = current_feature.geometry()
            next_feature_geom = next_feature.geometry()
            current_point = current_feature_geom.asPoint()
            next_point = next_feature_geom.asPoint()

            distance_area = QgsDistanceArea()
            distance_area.setEllipsoid('WGS84')
            distance = distance_area.measureLine(current_point, next_point)
            wp_data_x.append(s)
            s += distance

            sample_interval = 1000 # every 1000 meters

            line = distance_area.geodesicLine(current_point, next_point,sample_interval)

            for point in line[0][0:-1]:
                points.append(point)

        wp_data_x.append(s)
        points.append(features[-1].geometry().asPoint())

        for i in range(len(points) - 1):
            current_point = points[i]
            next_point = points[i + 1]
            distance_area = QgsDistanceArea()
            distance_area.setEllipsoid('WGS84')
            distance = distance_area.measureLine(current_point, next_point)
            current_point = transform_to_raster_crs.transform(current_point)
            next_point = transform_to_raster_crs.transform(next_point)

            current_x = current_point.x()
            current_y = current_point.y()

            next_x = next_point.x()
            next_y = next_point.y()

            px, py = world_to_pixel(current_point.x(), current_point.y(), gt)

            # Read raster value
            gdal_raster = gdal.Open(raster_path)
            band = gdal_raster.GetRasterBand(band_number)
            raster_value = band.ReadAsArray(px, py, 1, 1)[0][0]

            data_x.append(total_distance)
            data_y.append(raster_value)

            total_distance += distance

        current_point = transform_to_raster_crs.transform(points[-1])
        px, py = world_to_pixel(current_point.x(), current_point.y(), gt)

        # Read raster value
        gdal_raster = gdal.Open(raster_path)
        band = gdal_raster.GetRasterBand(band_number)
        raster_value = band.ReadAsArray(px, py, 1, 1)[0][0]

        data_x.append(total_distance)
        data_y.append(raster_value)

        # ________________________________
        max_climbing_rate_feet = 700.0 # get from settings later !!!!!
        max_climbing_rate_meters = max_climbing_rate_feet / 3.28
        flight_speed_kmh = 200 # get from settings later !!!!!

        danger_points = []
        for i in range(len(data_x) - 1):
            x_distance = data_x[i + 1] - data_x[i]
            max_height_gain = max_climbing_rate_meters / ((flight_speed_kmh * 1000 / 60) / x_distance)
            y_distance = data_y[i + 1] - data_y[i]
            if max_height_gain <= y_distance:
                danger_points.append(i)
                #danger_points.append(i + 1)

        #1 / 0

        # ________________________________
        a = PlotDock(self.iface, data_x, data_y, wp_data_x, danger_points)

def world_to_pixel(x, y, gt):
    px = int((x - gt[0]) / gt[1])
    py = int((y - gt[3]) / gt[5])  # Negative y resolution
    return px, py