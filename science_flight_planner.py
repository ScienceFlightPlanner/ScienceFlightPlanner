# -*- coding: utf-8 -*-
"""
ScienceFlightPlanner - A QGIS plugin to create flight plans based on existing waypoints and paths.
Copyright (C) 2023 Leon Krüger, Lars Reining, Jonas Schröter, Moritz Vogel, Hannah Willkomm <scienceflightplanner@gmail.com>

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
import typing
from typing import List

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QToolButton, QMenu
# Initialize Qt resources from file resources.py
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QWidget

from .action_module import ActionModule
from .coverage_module import CoverageModule
from .flight_distance_duration_module import FlightDistanceDurationModule

# Initialize Qt resources from file resources.py
from .help_module import HelpManualModule
from .options_widget import SfpOptionsFactory
from .resources import *
from .utils import LayerUtils
from .waypoint_generation_module import WaypointGenerationModule
from .export_module import ExportModule
from .waypoint_tag_module import WaypointTagModule
from functools import partial

from .waypoint_reduction_module import WaypointReductionModule
from .waypoint_reversal_module import WaypointReversalModule

icon_folder_path = ":resources"

class ScienceFlightPlanner:
    """QGIS Plugin Implementation."""
    popupMenu: QMenu
    toolButton: QToolButton
    iface: QgisInterface
    plugin_dir: str
    actions: List[QAction]
    tag_actions: List[QAction]
    pluginMenu: QMenu
    toolbar: QToolBar
    pluginIsActive: bool
    layer_utils: LayerUtils
    flight_distance_duration_module: FlightDistanceDurationModule
    waypoint_generation_module: WaypointGenerationModule
    export_module: ExportModule
    waypoint_tag_module: WaypointTagModule
    waypoint_reduction_module: WaypointReductionModule
    waypoint_reversal_module: WaypointReversalModule
    coverage_module: CoverageModule
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
        #self.iface.mainWindow().setAttribute(Qt.WA_AlwaysShowToolTips, True)

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # Declare instance attributes
        self.actions = []
        self.tag_actions = []
        self.options_factory = None
        self.pluginMenu = self.iface.pluginMenu().addMenu(QIcon(":icon.png"), "&ScienceFlightPlanner")
        self.toolbar = self.iface.addToolBar("ScienceFlightPlanner")
        if self.toolbar:
            self.toolbar.setObjectName("ScienceFlightPlanner")

        self.pluginIsActive = False

        self.layer_utils = LayerUtils(iface)
        self.flight_distance_duration_module = FlightDistanceDurationModule(iface)
        self.waypoint_generation_module = WaypointGenerationModule(iface)
        self.export_module = ExportModule(iface)
        self.waypoint_tag_module = WaypointTagModule(iface)
        self.waypoint_reduction_module = WaypointReductionModule(iface)
        self.waypoint_reversal_module = WaypointReversalModule(iface)
        self.coverage_module = CoverageModule(iface)
        self.action_module = ActionModule(iface)
        self.help_module = HelpManualModule(
            iface, self.coverage_module.sensor_combobox, self.plugin_dir
        )
        #self.iface.pluginMenu().triggered.connect(self.help_module.close)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: typing.Callable[..., None],
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: typing.Union[None, str] = None,
        whats_this: typing.Union[None, str] = None,
        parent: typing.Union[None, QWidget] =None,
        is_checkable: bool = False,
        connect: bool = True,
        append: bool = True,
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :param is_checkable: Flag indicating whether the action should be checkable

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        """
        if parent is None:
            parent = self.toolbar

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        if connect:
            action.triggered.connect(callback)

        action.setEnabled(enabled_flag)
        action.setCheckable(is_checkable)

        #if status_tip is not None:
            #action.setStatusTip(status_tip)

        #if whats_this is not None:
            #action.setWhatsThis(whats_this)
        print(action.toolTip() + " " + action.statusTip() + " " + action.whatsThis())

        if add_to_toolbar and self.toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.pluginMenu.addAction(action)

        if append:
            self.actions.append(action)

        return action

    def add_popup_menu_button(self):
        self.popupMenu = QMenu()
        tag_list = self.waypoint_tag_module.tags
        for tag in tag_list[0:len(tag_list) - 1]:
            action = self.add_action(
                        os.path.join(icon_folder_path, "icon_tag.png"),
                        text=tag,
                        callback=partial(self.waypoint_tag_module.tag, tag),
                        add_to_toolbar=False,
                        parent=self.popupMenu,
                        connect=True,
                        append=False
                    )
            self.popupMenu.addAction(action)
            len(tag_list) - 1

        self.popupMenu.addSeparator()

        action = self.add_action(
            os.path.join(icon_folder_path, "icon_custom_tag.png"),
            text=tag_list[len(tag_list) - 1],
            callback=partial(self.waypoint_tag_module.new_tag, self.popupMenu),
            add_to_toolbar=False,
            parent=self.popupMenu,
            connect=True,
            append=False
        )

        self.popupMenu.addAction(action)
        self.toolButton = QToolButton(self.iface.mainWindow())
        self.toolButton.setText("tag")
        self.toolButton.setMenu(self.popupMenu)
        self.toolButton.setToolTip("Add tag to selected waypoints")
        self.toolButton.installEventFilter(self.toolbar)
        self.toolButton.setPopupMode(QToolButton.InstantPopup)
        self.toolButton.setIcon(QIcon(":resources/icon_tag.png"))
        self.actions.append(self.toolButton)
        self.toolbar.addWidget(self.toolButton)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        """Add toolbar buttons"""
        self.add_action(
            os.path.join(icon_folder_path, "icon_distance.png"),
            text=self.action_module.distance,
            callback=self.flight_distance_duration_module.toggle_display_flight_distance,
            parent=self.iface.mainWindow(),
            is_checkable=True,
        )
        self.add_action(
            os.path.join(icon_folder_path, "icon_duration.png"),
            text=self.action_module.duration,
            callback=self.flight_distance_duration_module.toggle_display_flight_duration,
            parent=self.iface.mainWindow(),
            is_checkable=True,
        )
        self.add_action(
            os.path.join(icon_folder_path, "icon_file.png"),
            text=self.action_module.waypoint_generation,
            callback=self.waypoint_generation_module.generate_waypoints_shp_file_action,
            parent=self.iface.mainWindow(),
        )
        self.add_action(
            os.path.join(icon_folder_path, "icon_export.png"),
            text=self.action_module.export,
            callback=self.export_module.shapefile_to_wpt_and_gfp,
            parent=self.iface.mainWindow(),
        )
        self.add_popup_menu_button()
        self.add_action(
            os.path.join(icon_folder_path, "icon_highlight.png"),
            text=self.action_module.reduced_waypoint_selection,
            callback=self.waypoint_reduction_module.highlight_selected_waypoints,
            parent=self.iface.mainWindow(),
        )
        self.add_action(
            os.path.join(icon_folder_path, "icon_labels.png"),
            text=self.action_module.reduced_waypoint_generation,
            callback=self.waypoint_reduction_module.generate_significant_waypoints_shp_file_action,
            parent=self.iface.mainWindow(),
        )
        self.add_action(
            os.path.join(icon_folder_path, "icon_reverse.png"),
            text=self.action_module.reversal,
            callback=self.waypoint_reversal_module.reverse_waypoints_action,
            parent=self.iface.mainWindow(),
        )
        self.add_action(
            os.path.join(icon_folder_path, "icon_coverage_lines.png"),
            text=self.action_module.coverage_lines,
            callback=self.coverage_module.compute_optimal_coverage_lines,
            parent=self.iface.mainWindow(),
        )
        self.add_action(
            os.path.join(icon_folder_path, "icon_help.png"),
            text=self.action_module.help_manual,
            callback=self.help_module.open_help_manual,
            parent=self.iface.mainWindow(),
            is_checkable=True,
        )

        self.help_action = QAction(
            QIcon(os.path.join(":icon.png")),
            "Science Flight Planner",
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
        self.coverage_module.flight_altitude_spinbox.setToolTip(
            self.action_module.flight_altitude
        )
        self.coverage_module.sensor_combobox.setToolTip(
            self.action_module.sensor_coverage
        )

        self.action_module.connect(
            self.actions,
            [
                self.coverage_module.flight_altitude_spinbox,
                self.coverage_module.sensor_combobox,
            ],
        )

        self.help_module.set_actions(self.actions)

    # --------------------------------------------------------------------------
    #this function is probably dead code
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin is closed"""
        # disconnects
        print("test")
        self.help_module.close()
        #self.iface.pluginMenu().triggered.disconnect(self.help_module.close)
        self.coverage_module.close()
        self.flight_distance_duration_module.close()
        self.waypoint_reduction_module.close()
        self.action_module.close()
        self.pluginIsActive = False

    def unload(self):
        #TODO
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.help_module.close()
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)
        self.iface.pluginMenu().removeAction(self.pluginMenu.menuAction())

        self.iface.pluginHelpMenu().removeAction(self.help_action)
        del self.help_action

        for action in self.actions:
            #self.toolbar.removeAction(action)
            if isinstance(action, QAction):
                self.iface.removeToolBarIcon(action)

        # remove the toolbar
        del self.toolbar

    # --------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""
        if not self.pluginIsActive:
            self.pluginIsActive = True
