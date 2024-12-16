import codecs
import os
from typing import List, Union

from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidgetAction, QGridLayout, QBoxLayout, QScrollArea
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QAction,
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QToolButton
)

from .action_module import ActionModule

complete_manual_name = "Complete Manual"
help_action_name = "Help"
faq_action_name = "FAQ"


class HelpWidget(QDockWidget):

    iface: QgisInterface
    plugin_dir: str
    layout: QBoxLayout
    toolbars: List[QToolBar]
    adjusted: bool
    action_module: ActionModule
    sensor_combobox_plugin: QComboBox

    actions: List[Union[QAction, QToolButton]]
    faq_button: Union[QPushButton, None]
    default_action: Union[QAction, None]

    toolbar_widgets: List[QWidget]
    sensor_combobox: Union[QComboBox, None]
    separator_widget: QWidget
    text_widget: QWidget

    current_action_name: str

    last_action_index: int
    current_width: int
    toolbar_thresholds: List[int]

    def __init__(
        self,
        iface: QgisInterface,
        actions: List[Union[QAction, QToolButton]],
        sensor_combobox: QComboBox,
        plugin_dir: str,
    ):
        super().__init__("ScienceFlightPlanner - Help Manual", iface.mainWindow())
        self.iface = iface
        self.plugin_dir = plugin_dir

        self.toolbars = []
        self.adjusted = True

        self.action_module = ActionModule(iface)
        self.actions = []
        self.default_action = None
        self.init_actions(actions)

        self.sensor_combobox_plugin = sensor_combobox
        self.sensor_combobox = None
        self.faq_button = None
        self.toolbar_widgets = []

        self.current_action_name = ""
        self.text_widget = QWidget()

        self.init_gui()

        self.current_width = self.width()
        print("Width Self: " + str(self.current_width))
        self.toolbar_thresholds = []

    def init_gui(self):
        """inits gui, i.e. init toolbar and sets default action"""
        self.init_toolbar()
        self.update_widget()

        # default action is triggered after opening the help widget
        if self.default_action is not None:
            self.default_action.trigger()

        self.setMinimumWidth(self.toolbars[0].width()//2 + 1)
        self.setFeatures(QDockWidget.DockWidgetClosable)

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

    def close(self):
        """removes help widget from the dock widgets and disconnects signals"""
        #for action in self.actions:
            #action.setCheckable(False)

        self.iface.removeDockWidget(self)

    def update_widget(self):
        """updates text widget"""
        widget = QWidget(self)
        self.layout = QVBoxLayout(widget)
        for toolbar in self.toolbars:
            self.layout.addWidget(toolbar)

        self.layout.addWidget(self.text_widget)
        widget.setLayout(self.layout)
        self.setWidget(widget)

    def init_toolbar(self):
        """inits toolbar of the help widget"""
        self.toolbars.append(QToolBar("Help Widget Toolbar 0", self.iface.mainWindow()))
        self.toolbars[0].setObjectName("Help Widget Toolbar 0")

        self.toolbars.append(QToolBar("Help Widget Toolbar 1", self.iface.mainWindow()))
        self.toolbars[1].setObjectName("Help Widget Toolbar 1")
        self.toolbars[1].setVisible(False)

        self.add_actions_to_toolbar()
        self.add_widgets_to_toolbar()
        self.last_action_index = len(self.actions) - 1

    def init_actions(self, actions: List[Union[QAction, QToolButton]]):
        for action in actions:
            # set triggers so that when pressing the button the corresponding html text shows
            fct = self.get_corresponding_action_fct(action)
            action.triggered.connect(fct)
            action.setCheckable(True)

            # default action is set to the action displaying the complete manual
            if action.text() == complete_manual_name:
                self.default_action = action

            self.actions.append(action)

    def adjust_tool_bars_to_decreasing_width(self):
        print("adjust dec")
        action_to_be_moved = self.actions[self.last_action_index]

        self.toolbars[0].removeAction(action_to_be_moved)

        before_action = (
            None
            if self.last_action_index + 1 == len(self.actions)
            else self.actions[self.last_action_index + 1]
        )

        self.toolbars[1].insertAction(before_action, action_to_be_moved)
        action_to_be_moved.setParent(self.toolbars[1])

        if self.last_action_index == len(self.actions) - 1:
            self.toolbars[1].setVisible(True)
            self.layout.insertWidget(1, self.toolbars[1])

        self.last_action_index -= 1

        self.current_width = self.width()

        self.toolbar_thresholds.append(self.current_width)

        if len(self.toolbars[1].actions()) == len(self.actions) // 2:
            self.setMinimumWidth(self.width())

    def adjust_tool_bars_to_increasing_width(self):
        action_to_be_moved = self.actions[self.last_action_index + 1]

        self.toolbars[1].removeAction(action_to_be_moved)

        before_action = None if self.last_action_index >= 0 else self.actions[self.last_action_index]

        self.toolbars[0].insertAction(before_action, action_to_be_moved)
        action_to_be_moved.setParent(self.toolbars[0])

        if not self.toolbars[1].actions():
            self.toolbars[1].setVisible(False)
            self.layout.removeWidget(self.toolbars[1])

        del self.toolbar_thresholds[-1]

        self.last_action_index += 1

        print("adjust inc")

    def add_actions_to_toolbar(self):
        """adds actions to toolbar and sets default action to 'complete manual'"""
        for action in self.actions:
            action.setParent(self.toolbars[0])
            self.toolbars[0].addAction(action)

    def add_actions_toolbar2(self, actions: List[Union[QAction, QToolButton]]):
        """adds actions to toolbar and sets default action to 'complete manual'"""

        #toolbar = self.iface.mainWindow().findChild(QToolBar, "ScienceFlightPlanner")
        #tool_buttons = [x for x in toolbar.findChildren(QToolButton) if x.objectName() != "qt_toolbar_ext_button"]
        grid_widget = QWidget()
        layout = QGridLayout(grid_widget)
        i = 0
        assert self.toolbars[0] is not None
        for t in actions:
            t.setParent(self.toolbars[0])
            fct = self.get_corresponding_action_fct(t)
            print(fct)
            t.clicked.connect(fct)
            t.setCheckable(True)
            layout.addWidget(t, i // 6, i % 6)
            if t.text() == "Help":
                self.default_action = t
            i+=1

        self.toolbars[0].addWidget(grid_widget)

        #self.toolbar = self.iface.mainWindow().findChild(QToolBar, "mSelectionToolBar")
        #self.iface.mainWindow().findChild(QToolBar, "mSelectionToolBar").findChild(QToolButton, "qt_toolbar_ext_button")

    def add_widgets_to_toolbar(self):
        """adds widgets in widgets list to the toolbar"""
        assert self.toolbars[0] is not None

        sensor_widget_action = SensorWidgetAction(self)
        faq_widget_action = FAQWidgetAction(self)
        self.toolbars[0].addAction(sensor_widget_action)
        self.toolbars[0].addAction(faq_widget_action)
        self.actions.append(sensor_widget_action)
        self.actions.append(faq_widget_action)

    def add_sensor_widget(self):
        """adds a sensor widget to the toolbar widgets (widgets are drawn in the order that they are added to the widgets list)"""
        layout = QHBoxLayout()

        sensor_combobox = QComboBox()
        sensor_combobox.setToolTip(self.action_module.sensor_coverage)
        layout.addWidget(sensor_combobox)
        layout.setContentsMargins(2, 0, 10, 0)

        sensor_widget = QWidget()
        sensor_widget.setLayout(layout)

        sensor_combobox.addItem(self.sensor_combobox_plugin.currentText())
        sensor_combobox.highlighted.connect(self.fct_display_coverage)
        sensor_combobox.activated.connect(self.update_coverage_widget)

        self.toolbar_widgets.append(sensor_widget)
        self.sensor_combobox = sensor_combobox

    def add_separator(self):
        """adds a separator to the toolbar widgets (widgets are drawn in the order that they are added to the widgets list)"""
        separator_label = QLabel("|")
        layout = QHBoxLayout()
        layout.addWidget(separator_label)

        separator_widget = QWidget()
        separator_widget.setLayout(layout)
        return separator_widget

    def add_faq_widget(self):
        """adds a faq widget to the toolbar widgets (widgets are drawn in the order that they are added to the widgets list)"""
        faq_button = QPushButton(faq_action_name)
        faq_button.setStyleSheet("QPushButton {color: black}")
        faq_button.setToolTip("faq")
        faq_button.setAutoDefault(False)

        faq_button.setCheckable(True)
        layout = QHBoxLayout()
        layout.addWidget(faq_button)
        layout.setContentsMargins(10, 0, 0, 0)

        faq_widget = QWidget()
        faq_widget.setLayout(layout)
        faq_button.clicked.connect(self.fct_faq)
        self.toolbar_widgets.append(faq_widget)
        self.faq_button = faq_button

    def get_corresponding_action_fct(self, action: Union[QAction, QToolButton]):
        """returns the corresponding trigger function for the action"""
        return {
            self.action_module.distance: self.fct_distance,
            self.action_module.duration: self.fct_duration,
            self.action_module.waypoint_generation: self.fct_generate_waypoints,
            self.action_module.export: self.fct_export,
            self.action_module.tag: self.fct_tag,
            self.action_module.reduced_waypoint_selection: self.fct_mark_significant_waypoints,
            self.action_module.reduced_waypoint_generation: self.fct_generate_reduced_waypoints,
            self.action_module.reversal: self.fct_reverse_waypoints,
            self.action_module.coverage_lines: self.fct_optimal_coverage_lines,
            self.action_module.flowline: self.fct_flowline,
            self.action_module.racetrack: self.fct_racetrack,
            complete_manual_name: self.fct_complete_manual,
        }[action.text()]

    def fct_action(self, action_name: str):
        """general trigger function. When action is triggered and is not checked right now, the corresponding manual is displayed else the complete manual is displayed"""

        if self.faq_button is not None:
            actions = self.actions + [self.faq_button]
        else:
            actions = self.actions

        # default action is triggered when current action has been triggered already (given a default action exists)
        if action_name == self.current_action_name:
            default_action_name = (
                "default" if self.default_action is None else self.default_action.text()
            )

            if action_name != default_action_name:
                self.fct_action(default_action_name)
            else:
                set_checked_for_corresponding_action_button(action_name, actions, True)

        else:
            # update checkable to new selection
            set_checked_for_corresponding_action_button(
                self.current_action_name, actions, False
            )
            set_checked_for_corresponding_action_button(action_name, actions, True)

            # read corresponding html file
            action_html_name = action_name.replace(" ", "_").lower() + ".html"
            html_path = os.path.join(self.plugin_dir, "resources", "user_manual")

            file = None

            if action_html_name in [f for f in os.listdir(html_path)]:
                html_file = os.path.join(html_path, action_html_name)
                file = codecs.open(html_file, "r")
                html_string = file.read()
            else:
                html_string = ""

            # set text widget to corresponding text and update widget
            self.text_widget = create_text_widget(html_string)
            self.update_widget()

            if file is not None:
                file.close()

            self.current_action_name = action_name

    def fct_faq(self):
        """trigger function for 'faq'"""
        self.fct_action(faq_action_name)

    def fct_optimal_coverage_lines(self):
        """trigger function for 'compute optimal coverage lines'"""
        self.fct_action(self.action_module.coverage_lines)

    def fct_complete_manual(self):
        """trigger function for 'complete manual'"""
        self.fct_action(complete_manual_name)

    def fct_distance(self):
        """trigger function for 'display flight distance'"""
        self.fct_action(self.action_module.distance)

    def fct_display_coverage(self):
        """trigger function for 'select sensor'"""
        self.fct_action(self.action_module.sensor_coverage)

    def update_coverage_widget(self):
        """updates the coverage widget (necessary after selecting item so that there can be a new 'highlighted' signal)"""
        assert self.sensor_combobox is not None
        self.fct_display_coverage()
        self.sensor_combobox.clear()
        self.sensor_combobox.addItem(self.sensor_combobox_plugin.currentText())

    def fct_duration(self):
        """trigger functions for 'display expected flight duration'"""
        self.fct_action(self.action_module.duration)

    def fct_generate_waypoints(self):
        """trigger function for 'generate waypoints for flightplan'"""
        self.fct_action(self.action_module.waypoint_generation)

    def fct_export(self):
        """trigger function for 'export as wpt file'"""
        self.fct_action(self.action_module.export)

    def fct_tag(self):
        """trigger function for 'tag waypoint'"""
        self.fct_action(self.action_module.tag)

    def fct_flowline(self):
        """trigger function for 'Calculate flowlines'"""
        self.fct_action(self.action_module.flowline)

    def fct_racetrack(self):
        """trigger function for 'Convert grid to racetrack'"""
        self.fct_action(self.action_module.racetrack)

    def fct_mark_significant_waypoints(self):
        """trigger function for 'mark selected waypoints as significant'"""
        self.fct_action(self.action_module.reduced_waypoint_selection)

    def fct_generate_reduced_waypoints(self):
        """trigger function for 'generate reduced flightplan from significant waypoints'"""
        self.fct_action(self.action_module.reduced_waypoint_generation)

    def fct_reverse_waypoints(self):
        """trigger function for 'reverse waypoints'"""
        self.fct_action(self.action_module.reversal)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        toolbar_extension_button_2 = self.toolbars[1].findChild(QToolButton, "qt_toolbar_ext_button")
        if toolbar_extension_button_2 and toolbar_extension_button_2.isVisible():
            self.setMinimumWidth(event.oldSize().width())
            return

        toolbar_extension_button = self.toolbars[0].findChild(QToolButton, "qt_toolbar_ext_button")
        if toolbar_extension_button and toolbar_extension_button.isVisible():
            toolbar_extension_button.hide()
            self.adjust_tool_bars_to_decreasing_width()
        elif self.isVisible():
            toolbar_threshold_index = len(self.actions) - 2 - self.last_action_index
            if (0 <= toolbar_threshold_index < len(self.toolbar_thresholds)
                    and event.size().width() > self.toolbar_thresholds[toolbar_threshold_index]):
                self.adjust_tool_bars_to_increasing_width()

class HelpManualModule:

    iface: QgisInterface
    sensor_combobox: QComboBox
    plugin_dir: str

    actions: Union[List[Union[QAction, QToolButton]], None]
    help_action: Union[QAction, None]

    help_widget: Union[HelpWidget, None]

    def __init__(self, iface, sensor_combobox, plugin_dir):
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.sensor_combobox = sensor_combobox

        self.actions = None
        self.help_action = None

        self.help_widget = None

    def open_help_manual(self):
        """opens the help manual"""
        assert self.actions is not None and self.help_action is not None

        self.help_action.setChecked(True)

        # initialize help widgets
        if self.help_widget is None:
            self.help_widget = HelpWidget(
                self.iface, self.actions, self.sensor_combobox, self.plugin_dir
            )
            self.help_widget.visibilityChanged.connect(self.close)

        elif not self.help_widget.isVisible():
            self.help_widget = HelpWidget(
                self.iface, self.actions, self.sensor_combobox, self.plugin_dir
            )
        else:
            self.close()

    def close(self):
        """closes the module and disconnects signals"""
        assert self.help_action is not None and self.actions is not None
        if self.help_widget is not None:
            # TODO: the following Line throws "TypeError 'method' object is not connected"
            #       is this line even necessary?
            #self.help_widget.visibilityChanged.disconnect(self.close)
            self.help_action.setChecked(False)
            self.help_widget.close()

    def set_actions(self):
        """copies the given lists of actions and modifies it so that the help action corresponds to the complete manual actions"""
        toolbar = self.iface.mainWindow().findChild(QToolBar, "ScienceFlightPlanner")
        tool_buttons = [x for x in toolbar.findChildren(QToolButton) if x.objectName() != "qt_toolbar_ext_button"]
        self.actions = []

        # copy actions so that buttons in help widget are not linked to the ones in the plugin's toolbar
        for tool_button in tool_buttons:
            text = tool_button.text()
            parent = tool_button.parent()
            icon = tool_button.icon()
            tool_tip = tool_button.toolTip()

            action = QAction(icon, text, parent)
            if tool_tip is not None:
                action.setToolTip(tool_tip)

            # text of help action is changed to "complete manual"
            if text != help_action_name:
                self.actions.append(action)
            else:
                self.help_action = toolbar.findChild(QAction, help_action_name)
                action.setText(complete_manual_name)
                action.setToolTip(complete_manual_name)
                # assure that complete manual action is the first action in the help widget
                self.actions.insert(0, action)


def create_text_widget(html_str: str = "") -> QWidget:
    """creates texts widget containing the given html string"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    widget.setLayout(layout)

    web_view = QTextBrowser()
    web_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    web_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    web_view.setReadOnly(True)
    web_view.setOpenExternalLinks(True)
    web_view.setHtml(html_str)

    layout.addWidget(web_view)
    return widget


def set_checked_for_corresponding_action_button(
    action_txt: str, actions: List[Union[QAction, QToolButton]], checked: bool
):
    """sets the action button with the given text to checked/not checked depending on the parameter checked"""
    # TODO QPushButton (faq button)  keeps getting deleted, which throws an error here
    matching_actions = [action for action in actions if action.text() == action_txt]
    print("-------------")
    for action in matching_actions:
        print(str(action) + " : " + str(action.toolTip()))
    print("-------------")
    # if multiple action or no action matches no action is set checked
    if len(matching_actions) != 1:
        return

    action = matching_actions[0]

    if not action.isCheckable():
        return

    action.setChecked(checked)

class SensorWidgetAction(QWidgetAction):
    help_widget: Union[HelpWidget, None]

    def __init__(self, help_widget: HelpWidget):
        super().__init__(help_widget.toolbars[0])
        self.help_widget = help_widget
        self.setObjectName("SensorWidgetAction")
        super().setObjectName("SensorWidgetAction")

    def createWidget(self, parent):
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 0, 0, 0)

        sensor_combobox = QComboBox()
        sensor_combobox.setToolTip(self.help_widget.action_module.sensor_coverage)
        default_icon_height = self.help_widget.toolbars[0].iconSize().height()
        sensor_combobox.setFixedHeight(default_icon_height)
        layout.addWidget(sensor_combobox)

        sensor_combobox.addItem(self.help_widget.sensor_combobox_plugin.currentText())
        sensor_combobox.highlighted.connect(self.help_widget.fct_display_coverage)
        sensor_combobox.activated.connect(self.help_widget.update_coverage_widget)
        self.help_widget.sensor_combobox = sensor_combobox

        sensor_widget = QWidget(parent)
        sensor_widget.setLayout(layout)
        sensor_widget.setObjectName("SensorWidgetAction")
        return sensor_widget

class FAQWidgetAction(QWidgetAction):
    help_widget: Union[HelpWidget, None]

    def __init__(self, help_widget: HelpWidget):
        super().__init__(help_widget.toolbars[0])
        self.help_widget = help_widget
        self.setObjectName("FAQWidgetAction")
        super().setObjectName("FAQWidgetAction")

    def createWidget(self, parent):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        separator_layout = QHBoxLayout()
        separator_layout.setContentsMargins(15, 0, 10, 0)
        separator_label = QLabel("|")
        separator_layout.addWidget(separator_label)
        separator_widget = QWidget()
        separator_widget.setLayout(separator_layout)
        self.help_widget.separator_widget = separator_widget
        layout.addWidget(separator_widget)

        faq_button = QPushButton(faq_action_name)
        faq_button.setToolTip("faq")
        faq_button.setAutoDefault(False)
        faq_button.setCheckable(True)
        faq_button.clicked.connect(self.help_widget.fct_faq)
        default_icon_height = self.help_widget.toolbars[0].iconSize().height()
        faq_button.setFixedHeight(default_icon_height)
        self.help_widget.faq_button = faq_button
        layout.addWidget(faq_button)

        faq_widget = QWidget(parent)
        faq_widget.setLayout(layout)
        faq_widget.setObjectName("FAQWidgetAction")
        return faq_widget