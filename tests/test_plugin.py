import sys
import time
from typing import List

import qgis
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QToolBar, QToolButton, QAction, QDockWidget
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.utils import plugins, iface
from qgis.testing import unittest
import tempfile

# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.export_module import shapefile_to_wpt, wpt_to_gfp
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.help_module import HelpWidget


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

    def NOtest_unload2(self):
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

    def test_unload(self):
        print("ScienceFlightPlanner" in plugins)
        all_c = iface.mainWindow().children()
        settings = QSettings()
        settings.setValue("Plugins/ScienceFlightPlanner", False)
        qgis.utils.unloadPlugin("ScienceFlightPlanner")
        print("ScienceFlightPlanner" in plugins)
        updated_c = iface.mainWindow().children()
        print("List:")
        print(len(all_c))
        print(len(updated_c))
        for c in all_c:
            if c not in updated_c:
                print(str(c) + c.objectName() + c.toolTip())

        settings.setValue("Plugins/ScienceFlightPlanner", True)
        qgis.utils.loadPlugin("ScienceFlightPlanner")
        print("ScienceFlightPlanner" in plugins)
        updated_c = iface.mainWindow().children()

        print("List:")
        for c in updated_c:
            if c not in all_c:
                print(str(c) + c.objectName() + c.toolTip())

        qgis.utils.unloadPlugin("ScienceFlightPlanner")
        settings.setValue("Plugins/ScienceFlightPlanner", False)
        print("ScienceFlightPlanner" in plugins)

        print("List:")
        updated2_c = iface.mainWindow().children()
        for c in updated2_c:
            if c not in all_c:
                print(str(c) + c.objectName() + c.toolTip())
        print("END")

def run_all():
    """Default function that is called by the runner if nothing else is specified"""
    print("EXEC" + sys.executable)
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestPlugin, 'test'))
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite)