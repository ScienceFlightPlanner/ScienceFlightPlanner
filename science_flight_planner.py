# -*- coding: utf-8 -*-
"""ScienceFlightPlanner - A QGIS plugin to create flight plans based on existing waypoints and paths. Copyright (C)
2023 Leon Krüger, Lars Reining, Jonas Schröter, Moritz Vogel, Hannah Willkomm <scienceflightplanner@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os.path
from typing import List, Union, Callable

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QWidget, QToolButton, QMenu

from qgis.gui import QgisInterface

from .constants import (
    ICON_DIRECTORY_PATH,
    TAGS,
    CUSTOM_TAG,
    PLUGIN_NAME,
    PLUGIN_TOOLBAR_NAME,
    Q_TOOL_TIP_STYLE_SHEET,
    PLUGIN_HELP_MANUAL_TITLE,
    DISTANCE_ACTION_NAME,
    DURATION_ACTION_NAME,
    WAYPOINT_GENERATION_ACTION_NAME,
    COMBINE_FLIGHT_PLANS_ACTION_NAME,
    EXPORT_ACTION_NAME,
    TAG_ACTION_NAME,
    REDUCED_WAYPOINT_SELECTION_ACTION_NAME,
    REDUCED_WAYPOINT_GENERATION_ACTION_NAME,
    REVERSAL_ACTION_NAME,
    COVERAGE_LINES_ACTION_NAME,
    CUT_FLOWLINE_ACTION_NAME,
    RACETRACK_ACTION_NAME,
    TOPOGRAPHY_ACTION_NAME,
    HELP_MANUAL_ACTION_NAME,
    FLIGHT_ALTITUDE_ACTION_NAME,
    SENSOR_COVERAGE_ACTION_NAME,
    MAX_CLIMB_RATE_ACTION_NAME,
    PLUGIN_ICON_PATH
)
from .cut_flowline_module import CutFlowlineModule
from .racetrack_module import RacetrackModule
from .action_module import ActionModule
from .coverage_module import CoverageModule
from .flight_distance_duration_module import FlightDistanceDurationModule

# Not an Unused import statement!!!
# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences
from .resources import *
# Do not delete!!!

from .help_module import HelpManualModule
from .options_widget import SfpOptionsFactory
from .utils import LayerUtils
from .waypoint_generation_module import WaypointGenerationModule
from .combine_flightplans_module import CombineFlightplansModule
from .export_module import ExportModule
from .waypoint_tag_module import WaypointTagModule
from .topography_module import TopographyModule
from functools import partial

from .waypoint_reduction_module import WaypointReductionModule
from .waypoint_reversal_module import WaypointReversalModule


class ScienceFlightPlanner:
    """QGIS Plugin Implementation."""
    popupMenu: QMenu
    toolButton: QToolButton
    iface: QgisInterface
    toolbar_items: List[QObject]
    pluginMenu: QMenu
    toolbar: Union[QToolBar, None]
    pluginIsActive: bool
    layer_utils: LayerUtils
    flight_distance_duration_module: FlightDistanceDurationModule
    waypoint_generation_module: WaypointGenerationModule
    combine_flightplans_module: CombineFlightplansModule
    export_module: ExportModule
    waypoint_tag_module: WaypointTagModule
    waypoint_reduction_module: WaypointReductionModule
    waypoint_reversal_module: WaypointReversalModule
    coverage_module: CoverageModule
    cut_flowline_module: CutFlowlineModule
    racetrack_module: RacetrackModule
    topography_module: TopographyModule
    action_module: ActionModule

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        """
        # Save reference to the QGIS interface
        self.help_action = None
        self.iface = iface

        # Declare instance attributes
        self.toolbar_items = []
        self.options_factory = None
        self.pluginMenu = self.iface.pluginMenu().addMenu(QIcon(PLUGIN_ICON_PATH), PLUGIN_NAME)
        self.toolbar = self.iface.addToolBar(PLUGIN_TOOLBAR_NAME)
        if self.toolbar:
            self.toolbar.setObjectName(PLUGIN_TOOLBAR_NAME)

        self.toolbar.setStyleSheet(Q_TOOL_TIP_STYLE_SHEET)

        self.pluginIsActive = False

        self.layer_utils = LayerUtils(iface)
        self.flight_distance_duration_module = FlightDistanceDurationModule(iface)
        self.waypoint_generation_module = WaypointGenerationModule(iface)
        self.combine_flightplans_module = CombineFlightplansModule(iface)
        self.export_module = ExportModule(iface)
        self.waypoint_tag_module = WaypointTagModule(iface)
        self.waypoint_reduction_module = WaypointReductionModule(iface)
        self.waypoint_reversal_module = WaypointReversalModule(iface)
        self.coverage_module = CoverageModule(iface)
        self.racetrack_module = RacetrackModule(iface, self.coverage_module)
        self.topography_module = TopographyModule(iface)
        self.cut_flowline_module = CutFlowlineModule(iface)
        self.action_module = ActionModule(iface)
        self.help_module = HelpManualModule(
            iface, self.coverage_module.sensor_combobox
        )

    def add_action(
            self,
            icon: str,
            text: str,
            callback: Callable[..., None],
            enabled_flag: bool = True,
            add_to_menu: bool = True,
            add_to_toolbar: bool = True,
            parent: Union[None, QWidget] = None,
            is_checkable: bool = False
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon: Name of the icon file.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param parent: Parent widget for the new action. Defaults None.

        :param is_checkable: Flag indicating whether the action should be checkable

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        """
        if parent is None:
            parent = self.iface.mainWindow()

        icon_path = os.path.join(ICON_DIRECTORY_PATH, icon)
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.setObjectName(text)

        action.triggered.connect(callback)

        action.setEnabled(enabled_flag)
        action.setCheckable(is_checkable)

        if add_to_toolbar and self.toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.pluginMenu.addAction(action)

        self.toolbar_items.append(action)

        return action

    def add_popup_menu_button(self):
        self.popupMenu = QMenu()
        for tag in TAGS:
            action = self.add_action(
                icon="icon_tag.png",
                text=tag,
                callback=partial(self.waypoint_tag_module.tag, tag),
                add_to_toolbar=False,
                parent=self.popupMenu
            )
            action.setToolTip(TAG_ACTION_NAME)
            self.popupMenu.addAction(action)

        self.popupMenu.addSeparator()

        action = self.add_action(
            icon="icon_custom_tag.png",
            text=CUSTOM_TAG,
            callback=partial(self.waypoint_tag_module.new_tag, self.popupMenu),
            add_to_toolbar=False,
            parent=self.popupMenu
        )
        action.setToolTip(TAG_ACTION_NAME)
        self.popupMenu.addAction(action)

        self.toolButton = QToolButton(self.iface.mainWindow())
        icon_path = os.path.join(ICON_DIRECTORY_PATH, "icon_tag.png")
        self.toolButton.setIcon(QIcon(icon_path))
        self.toolButton.setText(TAG_ACTION_NAME)
        self.toolButton.setToolTip(TAG_ACTION_NAME)
        self.toolButton.setMenu(self.popupMenu)
        self.toolButton.installEventFilter(self.toolbar)
        self.toolButton.setPopupMode(QToolButton.InstantPopup)

        self.toolbar_items.append(self.toolButton)
        self.toolbar.addWidget(self.toolButton)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        """Add toolbar buttons"""
        self.add_action(
            icon="icon_distance.png",
            text=DISTANCE_ACTION_NAME,
            callback=self.flight_distance_duration_module.toggle_display_flight_distance,
            parent=self.toolbar,
            is_checkable=True,
        )
        self.add_action(
            icon="icon_duration.png",
            text=DURATION_ACTION_NAME,
            callback=self.flight_distance_duration_module.toggle_display_flight_duration,
            parent=self.toolbar,
            is_checkable=True,
        )
        self.add_action(
            icon="icon_file.png",
            text=WAYPOINT_GENERATION_ACTION_NAME,
            callback=self.waypoint_generation_module.generate_waypoints_shp_file_action,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_combine.png",
            text=COMBINE_FLIGHT_PLANS_ACTION_NAME,
            callback=self.combine_flightplans_module.combine,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_export.png",
            text=EXPORT_ACTION_NAME,
            callback=self.export_module.shapefile_to_wpt_and_gfp,
            parent=self.toolbar,
        )
        self.add_popup_menu_button()
        self.add_action(
            icon="icon_highlight.png",
            text=REDUCED_WAYPOINT_SELECTION_ACTION_NAME,
            callback=self.waypoint_reduction_module.highlight_selected_waypoints,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_labels.png",
            text=REDUCED_WAYPOINT_GENERATION_ACTION_NAME,
            callback=self.waypoint_reduction_module.generate_significant_waypoints_shp_file_action,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_reverse.png",
            text=REVERSAL_ACTION_NAME,
            callback=self.waypoint_reversal_module.reverse_waypoints_action,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_coverage_lines.png",
            text=COVERAGE_LINES_ACTION_NAME,
            callback=self.coverage_module.compute_optimal_coverage_lines,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_cut_flowline.png",
            text=CUT_FLOWLINE_ACTION_NAME,
            callback=self.cut_flowline_module.cut_action,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_racetrack.png",
            text=RACETRACK_ACTION_NAME,
            callback=self.racetrack_module.compute_way_points,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_topography.png",
            text=TOPOGRAPHY_ACTION_NAME,
            callback=self.topography_module.tmp,
            parent=self.toolbar,
        )
        self.add_action(
            icon="icon_help.png",
            text=HELP_MANUAL_ACTION_NAME,
            callback=self.help_module.open_help_manual,
            parent=self.toolbar,
            is_checkable=True,
        )

        self.help_action = QAction(
            QIcon(os.path.join(PLUGIN_ICON_PATH)),
            PLUGIN_HELP_MANUAL_TITLE,
            self.iface.mainWindow()
        )
        self.iface.pluginHelpMenu().addAction(self.help_action)
        self.help_action.triggered.connect(self.help_module.open_help_manual)

        self.options_factory = SfpOptionsFactory(
            self.flight_distance_duration_module, self.coverage_module
        )
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        self.flight_distance_duration_module.init_gui(self.toolbar)

        self.coverage_module.init_gui(self.toolbar)
        self.coverage_module.flight_altitude_spinbox.setToolTip(FLIGHT_ALTITUDE_ACTION_NAME)
        self.toolbar_items.append(self.coverage_module.flight_altitude_spinbox)

        self.coverage_module.sensor_combobox.setToolTip(SENSOR_COVERAGE_ACTION_NAME)
        self.toolbar_items.append(self.coverage_module.sensor_combobox)

        self.topography_module.init_gui(self.toolbar)
        self.topography_module.max_climb_rate_spinbox.setToolTip(MAX_CLIMB_RATE_ACTION_NAME)
        self.toolbar_items.append(self.topography_module.max_climb_rate_spinbox)

        self.action_module.connect(self.toolbar_items)

        self.help_module.set_actions()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.help_module.close()
        self.coverage_module.close()
        self.flight_distance_duration_module.close()
        self.waypoint_reduction_module.close()
        self.topography_module.close()
        self.action_module.close()
        self.pluginIsActive = False
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)
        self.iface.pluginMenu().removeAction(self.pluginMenu.menuAction())

        self.iface.pluginHelpMenu().removeAction(self.help_action)
        self.help_action = None

        self.toolbar = None

    # --------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""
        if not self.pluginIsActive:
            self.pluginIsActive = True
