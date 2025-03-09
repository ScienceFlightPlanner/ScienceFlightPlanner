import os

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject, QgsSettings
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLineEdit, QPushButton

from .constants import (
    PLUGIN_SENSOR_SETTINGS_PATH,
    PLUGIN_OVERLAP_SETTINGS_PATH,
    PLUGIN_OVERLAP_ROTATION_SETTINGS_PATH,
    PLUGIN_NAME,
    PLUGIN_ICON_PATH,
    DEFAULT_PUSH_MESSAGE_DURATION,
    PLUGIN_DIRECTORY_PATH
)
from .coverage_module import CoverageModule
from .flight_distance_duration_module import FlightDistanceDurationModule
from .utils import show_checkable_info_message_box

# from PyQt import uic
WIDGET, BASE = uic.loadUiType(os.path.join(PLUGIN_DIRECTORY_PATH, "options.ui"))


class SfpOptionsFactory(QgsOptionsWidgetFactory):
    flight_distance_duration_module: FlightDistanceDurationModule
    coverage_module: CoverageModule

    def __init__(
        self,
        flight_distance_duration_module: FlightDistanceDurationModule,
        coverage_module: CoverageModule,
    ):
        super().__init__(PLUGIN_NAME, QIcon(PLUGIN_ICON_PATH))
        self.flight_distance_duration_module = flight_distance_duration_module
        self.coverage_module = coverage_module

    def createWidget(self, parent: None = None):
        return SfpConfigOptionsPage(
            parent, self.flight_distance_duration_module, self.coverage_module
        )


class SfpConfigOptionsPage(QgsOptionsPageWidget):
    flight_distance_duration_module: FlightDistanceDurationModule

    def __init__(
        self,
        parent,
        flight_distance_duration_module: FlightDistanceDurationModule,
        coverage_module: CoverageModule,
    ):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.config_widget = OptionsDialog(coverage_module)
        layout.addWidget(self.config_widget)
        self.setObjectName("processingOptions")
        self.flight_distance_duration_module = flight_distance_duration_module

    def apply(self):
        try:
            self.config_widget.accept()
        except ValueError as err:
            self.flight_distance_duration_module.iface.messageBar().pushMessage(
                "Couldn't save changes",
                str(err.args[0]),
                level=Qgis.MessageLevel.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
        self.flight_distance_duration_module.update_flight_distance_duration_widgets()


class OptionsDialog(BASE, WIDGET):
    coverage_module: CoverageModule

    def __init__(self, coverage_module: CoverageModule):
        super().__init__()
        self.settings = QgsSettings()
        self.setupUi(self)
        self.proj = QgsProject.instance()
        default_speed = 200
        flight_speed = self.proj.readDoubleEntry(
            PLUGIN_NAME, "flight_speed", default_speed
        )[0]
        self.flightSpeedSpinBox.setValue(int(flight_speed))
        txt = ("ScienceFlightPlanner \n\nThe sensor coverage works if the CRS used for computation and the project CRS "
               "are the same. \n\nWhen using a different CRS the sensor coverage shown might contain inconsistencies "
               "because of the line representation used in QGIS.")
        settings_name = "show_coverage_info"
        show_checkable_info_message_box(settings_name, txt, self.proj)

        coverage_crs = QgsCoordinateReferenceSystem(
            self.proj.readEntry(PLUGIN_NAME, "coverage_crs", None)[0]
        )
        self.coverageCrsWidget.setCrs(coverage_crs)
        default_overlap = 0
        self.overlapSpinBox.setSingleStep(0.01)
        self.overlapSpinBox.setMaximum(0.99)
        self.overlapSpinBox.setValue(
            float(
                self.settings.value(PLUGIN_OVERLAP_SETTINGS_PATH, default_overlap)
            )
        )
        self.overlapComboBox.addItem("optimal")
        self.overlapComboBox.addItem("90° rotated")
        self.overlapComboBox.setCurrentIndex(
            int(self.settings.value(PLUGIN_OVERLAP_ROTATION_SETTINGS_PATH, 0))
        )
        # self.overlapComboBox.currentText()
        self.sensors = self.settings.value(PLUGIN_SENSOR_SETTINGS_PATH, {})
        self.load_sensor_table()
        self.coverage_module = coverage_module

        default_max_turn_distance = 3500

        max_turn_distance = self.proj.readDoubleEntry(
            PLUGIN_NAME, "max_turn_distance", default_max_turn_distance
        )[0]
        self.maxTurnDistanceSpinBox.setValue(int(max_turn_distance))
        self.maxTurnDistanceSpinBox.setMaximum(100000)
        self.maxTurnDistanceSpinBox.setMinimum(0)

    def load_sensor_table(self):
        """Creates the table on the settings page which allows to manage (add, delete, edit) sensors"""
        self.clear_sensor_table()
        row = 1
        for sensor_name, sensor_angle in self.sensors.items():
            self.gridLayout.addWidget(QLineEdit(sensor_name, self), row, 0)
            spinBox = QDoubleSpinBox(self)
            spinBox.setMaximum(180)
            spinBox.setValue(sensor_angle)
            self.gridLayout.addWidget(spinBox, row, 1)
            delete_button = QPushButton("Delete", self)
            delete_button.setAccessibleName(sensor_name)
            delete_button.clicked.connect(self.delete_sensor)
            self.gridLayout.addWidget(delete_button, row, 2)
            row += 1
        self.gridLayout.addWidget(QLineEdit("", self), row, 0)
        spinBox = QDoubleSpinBox(self)
        spinBox.setMaximum(180)
        self.gridLayout.addWidget(spinBox, row, 1)
        add_button = QPushButton("Add new sensor", self)
        add_button.setAccessibleName("add new sensor")
        add_button.clicked.connect(lambda: self.add_sensor(row))
        self.gridLayout.addWidget(add_button, row, 2)

    def clear_sensor_table(self):
        for row in range(1, self.gridLayout.rowCount()):
            self.gridLayout.setRowStretch(row, 0)
            for col in range(self.gridLayout.columnCount()):
                item = self.gridLayout.itemAtPosition(row, col)
                if item:
                    widget_to_remove = item.widget()
                    widget_to_remove.setParent(None)
                    widget_to_remove.deleteLater()

    def add_sensor(self, row: int):
        """Adds a sensor to the sensor table.

        Parameters
        ----------
        row : int
            Row of the table in which the information (name and angle) of the new sensor can be found.
        """
        sensor_name = self.gridLayout.itemAtPosition(row, 0).widget().text()
        if sensor_name == "" or sensor_name in self.sensors.keys():
            return
        self.sensors[sensor_name] = (
            self.gridLayout.itemAtPosition(row, 1).widget().value()
        )
        self.load_sensor_table()

    def delete_sensor(self):
        """Deletes the sensor from the sensors which is connected to the button calling this method."""
        sensor_name = self.sender().accessibleName()
        self.sensors.pop(sensor_name)
        self.load_sensor_table()

    def accept(self):
        # update sensors
        names = []
        self.sensors = {}
        for row in range(1, self.gridLayout.rowCount()):
            item = self.gridLayout.itemAtPosition(row, 0)
            if item:
                if (
                    self.gridLayout.itemAtPosition(row, 2).widget().accessibleName()
                    == "add new sensor"
                ):
                    break
                name_widget = self.gridLayout.itemAtPosition(row, 0).widget()
                sensor_name = name_widget.text()
                if sensor_name in names or sensor_name == "":
                    raise ValueError("Invalid sensor name")
                else:
                    names.append(sensor_name)
                angle_widget = self.gridLayout.itemAtPosition(row, 1).widget()
                self.sensors[sensor_name] = angle_widget.value()

        self.proj.writeEntryDouble(
            PLUGIN_NAME,
            "max_turn_distance",
            self.maxTurnDistanceSpinBox.value()
        )

        self.proj.writeEntryDouble(
            PLUGIN_NAME, "flight_speed", self.flightSpeedSpinBox.value()
        )
        self.proj.writeEntry(
            PLUGIN_NAME,
            "coverage_crs",
            self.coverageCrsWidget.crs().authid(),
        )
        self.settings.setValue(
            PLUGIN_OVERLAP_SETTINGS_PATH, self.overlapSpinBox.value()
        )
        self.settings.setValue(
            PLUGIN_OVERLAP_ROTATION_SETTINGS_PATH,
            self.overlapComboBox.currentIndex(),
        )
        self.proj.writeEntryDouble(
            PLUGIN_NAME,
            "max_turn_distance",
            self.maxTurnDistanceSpinBox.value()
        )
        self.settings.setValue(PLUGIN_SENSOR_SETTINGS_PATH, self.sensors)
        self.coverage_module.set_sensor_combobox_entries()
        self.coverage_module.sensor_coverage_sensor_settings_changed()