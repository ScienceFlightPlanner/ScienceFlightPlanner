from qgis.gui import QgisInterface

from .utils import LayerUtils

class RacetrackModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def method(self):
        print("RacetrackModule method called")