from typing import List, Union

from qgis.core import (
    Qgis,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsProject,
    QgsSettings,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QHBoxLayout, QLabel, QToolBar, QWidget

from .constants import PLUGIN_NAME
from .utils import LayerUtils


class FlightDistanceDurationModule:
    iface: QgisInterface
    settings: QgsSettings
    layer_utils: LayerUtils
    proj: QgsProject

    distance_duration_widget: QWidget
    distance_duration_label: QLabel

    current_layer: Union[
        QgsVectorLayer, None
    ]  # Used in case multiple/none selection becomes valid after "selectionChanged" signal
    current_feature_id: Union[int, None]

    is_displaying_flight_distance: bool
    is_displaying_flight_duration: bool

    def __init__(self, iface: QgisInterface):
        self.iface = iface

        self.settings = QgsSettings()
        self.layer_utils = LayerUtils(iface)
        self.proj = QgsProject.instance()

        self.distance_duration_widget = QWidget()
        self.distance_duration_label = QLabel()
        self.init_widget()

        self.current_layer = None
        self.current_feature_id = None

        self.is_displaying_flight_distance = False
        self.is_displaying_flight_duration = False

    def init_gui(self, toolbar: QToolBar):
        """inits gui and connects time event handler for changes, e.g. concerning layer/feature selection"""
        toolbar.addWidget(self.distance_duration_widget)
        self.iface.currentLayerChanged.connect(self.handle_current_layer_changed)

    def close(self):
        """closes module and disconnects time event handler"""
        self.iface.currentLayerChanged.disconnect(self.handle_current_layer_changed)
        self.unset_flightplan_feature()
        self.set_layer_with_signals()

    def init_widget(self):
        """inits gui for displaying distance/duration"""
        layout = QHBoxLayout()
        layout.addWidget(self.distance_duration_label)
        layout.setContentsMargins(15, 0, 15, 0)
        self.distance_duration_widget.setLayout(layout)

    def compute_flight_distance(self, layer: QgsVectorLayer, feature_id: int) -> float:
        """Computes the length (in m) of the given feature in the given layer and return ir. If the feature geometry is not of type LineGeometry an according warning is thrown and 0 is returned."""
        feature = layer.getFeature(feature_id)
        if feature.geometry().type() != QgsWkbTypes.GeometryType.LineGeometry:
            self.iface.messageBar().pushMessage(
                "Couldn't perform calculation",
                f"Selected feature is of type {QgsWkbTypes.displayString(feature.geometry().wkbType())} but needs to be of type {QgsWkbTypes.displayString(QgsWkbTypes.Type.LineString)}.",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )
            return 0

        # Needs to be done because QGIS does not consider the distance unit setting
        # when evaluating the "$length" expression in a language except english
        project_distance_unit = QgsProject.instance().distanceUnits()
        QgsProject.instance().setDistanceUnits(QgsUnitTypes.DistanceUnit.DistanceMeters)
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
        context.setFeature(feature)

        unit_factor = QgsUnitTypes.fromUnitToUnitFactor(
            QgsUnitTypes.DistanceUnit.DistanceMeters,
            QgsUnitTypes.DistanceUnit.DistanceKilometers,
        )

        length = QgsExpression("$length").evaluate(context) * unit_factor
        QgsProject.instance().setDistanceUnits(project_distance_unit)
        return length

    def compute_flight_duration(
        self, layer: QgsVectorLayer, feature_id: int, flight_speed: float
    ) -> float:
        """Computes the flight duration (in h) for a given flight speed (in km/h) and returns it."""
        if flight_speed <= 0:
            self.iface.messageBar().pushMessage(
                "Couldn't perform calculation",
                "Flight speed must be greater than zero.",
                level=Qgis.MessageLevel.Warning,
                duration=4,
            )
            return 0

        flight_distance = self.compute_flight_distance(layer, feature_id)
        return flight_distance / flight_speed

    def update_flight_distance_duration_widgets(self):
        """Updates the text of the label in the toolbar that displays the flight speed and duration."""
        if self.current_feature_id is None:
            return

        distance_duration_text = ""
        if self.is_displaying_flight_distance:
            distance = self.compute_flight_distance(
                self.current_layer, self.current_feature_id
            )
            distance_duration_text = f"Distance: {distance:.2f}km"
        default_speed = 200
        if self.is_displaying_flight_duration:
            try:
                flight_speed = self.proj.readDoubleEntry(
                    PLUGIN_NAME, "flight_speed", default_speed
                )[0]
            except:
                self.iface.messageBar().pushMessage(
                    "Couldn't update flight duration",
                    "The flight speed setting is invalid.",
                    level=Qgis.MessageLevel.Warning,
                    duration=4,
                )
                return
            duration = self.compute_flight_duration(
                self.current_layer, self.current_feature_id, flight_speed
            )
            if len(distance_duration_text) > 0:
                distance_duration_text += " | "
            distance_duration_text += f"Duration: {duration:.2f}h"

        self.distance_duration_label.setText(distance_duration_text)

    def set_flightplan_feature(self):
        """
        Sets the currently selected feature to be used for displaying the flight
        distance and duration. If a feature is already set, it is first unset.
        Also sets the current layer on which the display might be possible
        (if layer invalid for feature set to None).
        """
        if self.current_feature_id is not None:
            self.unset_flightplan_feature()

        # necessary for checking for updates in feature selection in case of invalid feature selection
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.LineGeometry]
        )

        if selected_layer is None:
            return

        self.set_layer_with_signals(selected_layer)

        feature = self.layer_utils.get_selected_feature_from_layer(self.current_layer)

        if feature is None:
            return

        # only set if layer valid for distance/duration display
        self.current_feature_id = feature.id()
        self.update_flight_distance_duration_widgets()

    def unset_flightplan_feature(self):
        """
        Unsets the feature to be used for displaying the flight distance and duration.
        Does nothing if no feature is selected.
        """
        if self.current_feature_id is None:
            return

        self.current_feature_id = None
        self.distance_duration_label.clear()

    def set_layer_with_signals(self, layer: Union[QgsVectorLayer, None] = None):
        """connects signals to new layer and disconnects from previous in case of a layer change"""

        # no changes
        if self.current_layer == layer:
            return

        # disconnect signals of previous layer
        try:
            if self.current_layer is not None:
                self.current_layer.willBeDeleted.disconnect(self.handle_deleted_layer)
                self.current_layer.featureDeleted.disconnect(
                    self.handle_feature_deleted
                )
                self.current_layer.geometryChanged.disconnect(
                    self.update_flight_distance_duration_widgets
                )
                self.current_layer.featureAdded.disconnect(self.handle_feature_added)
                self.current_layer.selectionChanged.disconnect(
                    self.handle_selection_changed
                )
        except:
            pass

        # connect signals to new layer
        if layer is not None:
            layer.willBeDeleted.connect(self.handle_deleted_layer)
            layer.featureDeleted.connect(self.handle_feature_deleted)
            layer.geometryChanged.connect(self.update_flight_distance_duration_widgets)
            layer.featureAdded.connect(self.handle_feature_added)
            layer.selectionChanged.connect(self.handle_selection_changed)

        # set attribute for current layer accordingly
        self.current_layer = layer

    def set_layer_to_selected(self):
        layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.LineGeometry], display_error_messages=False
        )
        if layer is None:
            self.unset_flightplan_feature()
            self.set_layer_with_signals()
        else:
            self.set_flightplan_feature()

    def handle_deleted_layer(self):
        """handler for the QgsVectorLayer.willBeDeleted signal"""
        self.unset_flightplan_feature()
        QTimer().singleShot(0, self.set_layer_to_selected)

    def handle_current_layer_changed(self):
        """handles the change in the currently selected layer. If a new layer of type linegeometry is selected. The new distance/duration is displayed. Otherwise the display is cleared"""
        if self.is_displaying_flight_distance or self.is_displaying_flight_duration:
            QTimer().singleShot(0, self.set_layer_to_selected)

    def handle_feature_deleted(self, id: int):
        """
        Handler for the QgsVectorLayer.featureDeleted signal.
        Sets flight plan feature if it is the only one in layer, remove otherwise.
        """

        def deferred():
            if self.current_layer is None:
                return

            features = list(self.current_layer.getFeatures())
            if len(features) == 1:
                self.set_flightplan_feature()
            else:
                self.unset_flightplan_feature()

        QTimer().singleShot(0, deferred)

    def handle_feature_added(self, id: int):
        """
        Handler for the QgsVectorLayer.featureAdded signal.
        Sets flight plan feature if it is the only one in layer, remove otherwise.
        """

        def deferred():
            if self.current_layer is None:
                return

            features = list(self.current_layer.getFeatures())
            if len(features) == 1:
                self.set_flightplan_feature()
            else:
                self.unset_flightplan_feature()

        QTimer().singleShot(0, deferred)

    def handle_selection_changed(
        self, selected: List[int], deselected: List[int], clear_and_select: bool
    ):
        """
        Handler for the QgsVectorLayer.selectionChanged signal.
        Sets flight plan to newly selected feature.
        """
        if self.current_layer is None:
            QTimer().singleShot(0, self.unset_flightplan_feature)
        else:
            QTimer().singleShot(0, self.set_flightplan_feature)

    def toggle_display_flight_distance(self):
        """Toggles displaying the flight distance and resets or unsets the currently used flight plan feature."""
        self.is_displaying_flight_distance = not self.is_displaying_flight_distance

        if (
            not self.is_displaying_flight_distance
            and not self.is_displaying_flight_duration
        ):
            self.set_layer_with_signals()
        else:
            self.set_layer_to_selected()

        self.update_flight_distance_duration_widgets()

    def toggle_display_flight_duration(self):
        """Toggles displaying the flight duration and resets or unsets the currently used flight plan feature."""
        self.is_displaying_flight_duration = not self.is_displaying_flight_duration

        if (
            not self.is_displaying_flight_distance
            and not self.is_displaying_flight_duration
        ):
            self.set_layer_with_signals()
        else:
            self.set_layer_to_selected()

        self.update_flight_distance_duration_widgets()
