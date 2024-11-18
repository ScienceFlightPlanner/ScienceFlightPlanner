from typing import List

from qgis.core import Qgis, QgsPointXY, QgsVectorLayer, QgsWkbTypes
from qgis.gui import QgisInterface

from .utils import LayerUtils

import geopandas as gpd


class ExportModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def shapefile_to_geojson(self):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )

        if selected_layer is None:
            return

        shapefile_path = selected_layer.dataProvider().dataSourceUri().split('|')[0]
        print(shapefile_path)
        print(selected_layer.dataProvider().dataSourceUri())
        print(selected_layer.dataProvider().dataSourceUri().split('|'))

        gdf = gpd.read_file(shapefile_path)
        path_as_array = selected_layer.dataProvider().dataSourceUri().split('/')
        shapefile_name = path_as_array[-1]
        output_file_path = shapefile_path.replace(shapefile_name, "tmp.geojson")
        gdf.to_file(output_file_path, driver='GeoJSON')

    def shapefile_to_wpt(self):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        for f in selected_layer.getFeatures():
            geometry = f.geometry()
            geometry_single_type = QgsWkbTypes.isSingleType(geometry.wkbType())
            print(geometry.asPoint())
            print(f.attributes())
            f.setAttribute("id", "1 || '\n' || up")
            print(f.attributes())
            break

