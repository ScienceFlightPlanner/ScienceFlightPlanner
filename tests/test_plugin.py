import sys
import time
from typing import List

import qgis
from PyQt5.QtWidgets import QToolBar, QToolButton, QAction
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.utils import plugins, iface
from qgis.testing import unittest
import tempfile

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.export_module import shapefile_to_wpt, wpt_to_gfp


class TestPlugin(unittest.TestCase):
    plugin_instance: ScienceFlightPlanner

    layers: List[QgsVectorLayer]

    toolbar: QToolBar

    buttons: List[QToolButton]

    def setUp(self):
        self.plugin_instance = plugins["ScienceFlightPlanner"]
        self.layers = []
        self.toolbar = self.plugin_instance.toolbar
        self.buttons = self.toolbar.findChildren(QToolButton)

    def test_unload(self):
        print(qgis.utils.plugins)
        #for b in self.toolbar.findChildren(QToolButton):
        #    print(str(b) + b.toolTip() + b.objectName())

        qgis.utils.unloadPlugin("ScienceFlightPlanner")
        #for b in self.toolbar.findChildren(QToolButton):
        #    print(str(b) + b.toolTip() + b.objectName())

        self.assertTrue("ScienceFlightPlanner" not in qgis.utils.plugins)
        print(qgis.utils.plugins)
        for c in iface.mainWindow().findChildren(QToolBar):
            print(str(c) + c.objectName())

        print(qgis.utils.plugins)

def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    print("EXEC" + sys.executable)
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestPlugin, 'test'))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)