PLUGIN_NAME = "ScienceFlightPlanner"

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

SENSOR_COMBOBOX_DEFAULT_VALUE = "No sensor"
FIRST_ALGO_NAME = "Meander"
SECOND_ALGO_NAME = "Racetrack"
