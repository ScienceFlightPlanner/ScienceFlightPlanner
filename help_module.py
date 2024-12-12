import codecs
import os
from typing import List, Union

from PyQt5.QtWidgets import QToolButton
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
)

from .action_module import ActionModule

complete_manual_name = "Complete Manual"
help_action_name = "Help"
faq_action_name = "FAQ"


class HelpWidget(QDockWidget):

    iface: QgisInterface
    plugin_dir: str
    action_module: ActionModule
    sensor_combobox_plugin: QComboBox

    actions: List[Union[QAction, QToolButton]]
    faq_button: Union[QPushButton, None]
    default_action: Union[QAction, None]

    toolbar_widgets: List[QWidget]
    sensor_combobox: Union[QComboBox, None]
    text_widget: QWidget

    default_action: QAction
    current_action_name: str

    toolbar: QToolBar

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

        self.actions = actions
        self.action_module = ActionModule(iface)
        self.default_action = None

        self.sensor_combobox_plugin = sensor_combobox
        self.sensor_combobox = None
        self.faq_button = None
        self.toolbar_widgets = []

        self.current_action_name = ""
        self.text_widget = QWidget()

        self.init_gui()

    def init_gui(self):
        """inits gui, i.e. init toolbar and sets default action"""
        self.init_toolbar()
        self.update_widget()

        # default action is triggered after opening the help widget
        if self.default_action is not None:
            self.default_action.trigger()

        self.setMinimumWidth(self.toolbar.width() + 75)
        self.setFeatures(QDockWidget.DockWidgetClosable)

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

    def close(self):
        """removes help widget from the dock widgets and disconnects signals"""
        for action in self.actions:
            action.setCheckable(False)
        self.iface.removeDockWidget(self)

    def update_widget(self):
        """updates text widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_widget)
        widget.setLayout(layout)
        self.setWidget(widget)

    def init_toolbar(self):
        """inits toolbar of the help widget"""
        self.toolbar = QToolBar()

        self.add_actions_toolbar(self.actions)
        self.add_widgets_toolbar()

    def add_actions_toolbar(self, actions: List[Union[QAction, QToolButton]]):
        """adds actions to toolbar and sets default action to 'complete manual'"""
        assert self.toolbar is not None
        for action in actions:
            # set triggers so that when pressing the button the corresponding html text shows
            fct = self.get_corresponding_action_fct(action)
            action.triggered.connect(fct)
            action.setCheckable(True)
            self.toolbar.addAction(action)

            # default action is set to the action displaying the complete manual
            if action.text() == complete_manual_name:
                self.default_action = action

    def add_widgets_toolbar(self):
        """adds widgets in widgets list to the toolbar"""
        assert self.toolbar is not None
        self.add_sensor_widget()
        self.add_separator()
        self.add_faq_widget()

        for w in self.toolbar_widgets:
            self.toolbar.addWidget(w)

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
        self.toolbar_widgets.append(separator_widget)

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
            self.help_widget.visibilityChanged.disconnect(self.close)
            self.help_action.setChecked(False)
            self.help_widget.close()
            self.help_widget = None

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
            print(action.toolTip())


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
    matching_actions = [action for action in actions if action.text() == action_txt]
    # if multiple action or no action matches no action is set checked
    if len(matching_actions) != 1:
        return

    action = matching_actions[0]

    if not action.isCheckable():
        return

    action.setChecked(checked)
