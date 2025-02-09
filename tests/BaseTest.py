from abc import ABC
import random
random.seed(0)

from qgis.testing import unittest
from qgis.utils import plugins
# noinspection PyUnresolvedReferences
from ScienceFlightPlanner.science_flight_planner import ScienceFlightPlanner


class BaseTest(unittest.TestCase, ABC):
    plugin_instance: ScienceFlightPlanner

    def setUp(self):
        self.plugin_instance = plugins["ScienceFlightPlanner"]