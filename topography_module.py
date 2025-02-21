from osgeo import gdal
from qgis.core import QgsPointXY, QgsCoordinateTransform, QgsRasterLayer, QgsVectorLayer, QgsProject
from qgis.gui import QgisInterface

import numpy as np
import matplotlib.pyplot as plt

from .utils import LayerUtils

class TopographyModule:

    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def tmp(self):
        # Paths to files (update these)
        vector_path = r"C:\Users\maxim\OneDrive\Desktop\Bachelorpraktikum\BP-AdvancedScienceFlightPlanner\SLOGIS2024-Flight1\SLOGIS2024-Flight1_explainer.shp"
        raster_path = r"C:\Users\maxim\Downloads\DEM.tif"

        # Load shapefile
        vector_layer = QgsVectorLayer(vector_path, "Line Layer", "ogr")
        if not vector_layer.isValid():
            print("Error: Could not load vector layer")
            exit()

        # Load raster
        raster_layer = QgsRasterLayer(raster_path, "Raster Layer", "gdal")
        if not raster_layer.isValid():
            print("Error: Could not load raster layer")
            exit()

        # Get raster properties
        raster_provider = raster_layer.dataProvider()
        raster_transform = raster_layer.crs()
        band_number = 1  # Assuming single-band raster

        # Get line features
        line_features = vector_layer.getFeatures()

        profile_data = []

        x = 0

        for feature in line_features:
            geom = feature.geometry()

            if geom.isMultipart():
                lines = geom.asMultiPolyline()
            else:
                lines = [geom.asPolyline()]

            for line in lines:
                for point in line:
                    # Transform point to raster CRS
                    point = QgsPointXY(point)
                    transform = QgsCoordinateTransform(vector_layer.crs(), raster_transform, QgsProject.instance())
                    transformed_point = transform.transform(point)

                    # Convert coordinates to raster pixel index
                    pixel_x = int((
                                              transformed_point.x() - raster_provider.extent().xMinimum()) / raster_layer.rasterUnitsPerPixelX())
                    pixel_y = int((
                                              raster_provider.extent().yMaximum() - transformed_point.y()) / raster_layer.rasterUnitsPerPixelY())

                    x += transformed_point.x()
                    print(x)

                    # Read raster value
                    gdal_raster = gdal.Open(raster_path)
                    band = gdal_raster.GetRasterBand(band_number)
                    raster_value = band.ReadAsArray(pixel_x, pixel_y, 1, 1)[0][0]

                    profile_data.append((x, raster_value))  # Store X (distance) and Y (raster value)

        # Convert to NumPy array
        profile_data = np.array(profile_data)

        # **PLOTTING**
        plt.figure(figsize=(8, 4))
        plt.plot(profile_data[:, 0], profile_data[:, 1], color="blue", linewidth=2, label="Elevation Profile")
        plt.xlabel("Distance along line")
        plt.ylabel("Raster Value")
        plt.title("Profile from Raster")
        plt.grid(True)
        plt.legend()
        plt.show()
