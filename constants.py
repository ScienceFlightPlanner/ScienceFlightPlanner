import codecs
import os
from qgis.core import QgsSettings


def get_icon_directory_path():
    if QgsSettings().value("UI/UITheme", "default") == "Night Mapping":
        return os.path.join(":resources", "icons_for_dark_mode")
    else:
        return os.path.join(":resources", "icons_for_light_mode")


PLUGIN_NAME = "ScienceFlightPlanner"

PLUGIN_DIRECTORY_PATH = os.path.dirname(__file__)

ICON_DIRECTORY_PATH = get_icon_directory_path()

USER_MANUAL_HTMLS_DIRECTORY_PATH = os.path.join(PLUGIN_DIRECTORY_PATH, "resources", "user_manual")

DEFAULT_PUSH_MESSAGE_DURATION = 4 # in seconds

PLUGIN_ICON_PATH = ":icon.png"

PLUGIN_SENSOR_SETTINGS_PATH = "science_flight_planner/sensors"
PLUGIN_OVERLAP_SETTINGS_PATH = "science_flight_planner/overlap"
PLUGIN_OVERLAP_ROTATION_SETTINGS_PATH = "science_flight_planner/overlap_rotation"
PLUGIN_MAX_TURN_DISTANCE_SETTINGS_PATH = "science_flight_planner/max_turn_distance"

PLUGIN_TOOLBAR_NAME = "ScienceFlightPlanner Toolbar"

Q_TOOL_TIP_STYLE_SHEET = """
                        QToolTip {
                            font-weight: bold;
                        }
                    """

PLUGIN_HELP_MANUAL_TITLE = "Science Flight Planner - Help Manual"

# tag/comments in the .wpt file can be longer than 10 characters,
# but the GARMIN GTN750 Xi may be not able to fully display them
MAX_TAG_LENGTH = 10 # in chars

QGIS_FIELD_NAME_TAG = "tag"

QGIS_FIELD_NAME_ID = "id"

QGIS_FIELD_NAME_SIG = "sig"

TAGS = [
    "FLYOVER",
    "FLYBY",
    "RH180",
    "RH270",
    "LH180",
    "LH270",
]

CUSTOM_TAG = "Custom tag"

DEFAULT_TAG = TAGS[0]

DISTANCE_ACTION_NAME = "Display Flight Distance"
DURATION_ACTION_NAME = "Display Expected Flight Duration"
WAYPOINT_GENERATION_ACTION_NAME = "Generate Waypoints for Flightplan"
COMBINE_FLIGHT_PLANS_ACTION_NAME = "Combine Flightplans"
EXPORT_ACTION_NAME = "Export to Garmin"
TAG_ACTION_NAME = "Add tag to selected waypoints"
REDUCED_WAYPOINT_SELECTION_ACTION_NAME = "Mark Selected Waypoints as Significant"
REDUCED_WAYPOINT_GENERATION_ACTION_NAME = "Generate Reduced Flightplan from Significant Waypoints"
REVERSAL_ACTION_NAME = "Reverse Waypoints"
COVERAGE_LINES_ACTION_NAME = "Compute Optimal Coverage Lines"
FLOWLINE_ACTION_NAME = "Get flowline from file"
CUT_FLOWLINE_ACTION_NAME = "Cut flowline"
RACETRACK_ACTION_NAME = "Convert grid to racetrack"
TOPOGRAPHY_ACTION_NAME = "Create topography profile"
HELP_MANUAL_ACTION_NAME = "Help"
FLIGHT_ALTITUDE_ACTION_NAME = "Set Flight Altitude"
SENSOR_COVERAGE_ACTION_NAME = "Select Sensor"
MAX_CLIMB_RATE_ACTION_NAME = "Set Maximum Climb Rate"

SENSOR_COMBOBOX_DEFAULT_VALUE = "No sensor"
FIRST_ALGO_NAME = "Meander"
SECOND_ALGO_NAME = "Racetrack"


def create_html_str_for_action_dict():
    result = dict()
    for html_name in [file_name for file_name in os.listdir(USER_MANUAL_HTMLS_DIRECTORY_PATH) if file_name.endswith(".html")]:
        action_name = html_name.replace(".html", "").replace("_", " ")
        html_path = os.path.join(USER_MANUAL_HTMLS_DIRECTORY_PATH, html_name)
        with codecs.open(html_path, "r", encoding="utf-8") as file:
            html_string = file.read()
        html_string = html_string.replace("{ICON_FOLDER_PATH}", ICON_DIRECTORY_PATH)
        result[action_name] = html_string

    return result


HTML_FILE_FOR_ACTION = create_html_str_for_action_dict()
