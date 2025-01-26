PLUGIN_NAME = "ScienceFlightPlanner"

PLUGIN_TOOLBAR_NAME = "ScienceFlightPlanner Toolbar"

Q_TOOL_TIP_STYLE_SHEET = """
                        QToolTip {
                            font-weight: bold;
                        }
                    """

PLUGIN_HELP_MANUAL_TITLE = "Science Flight Planner - Help Manual"

MAX_TAG_LENGTH = 10

QGIS_FIELD_NAME_TAG = "tag"

QGIS_FIELD_NAME_ID = "id"

QGIS_FIELD_NAME_SIG = "sig"

TAGS = [
    "fly-over",
    "fly-by",
    "RH 180",
    "RH 270",
    "LH 180",
    "LH 270",
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
HELP_MANUAL_ACTION_NAME = "Help"
FLIGHT_ALTITUDE_ACTION_NAME = "Set Flight Altitude"
SENSOR_COVERAGE_ACTION_NAME = "Select Sensor"

SENSOR_COMBOBOX_DEFAULT_VALUE = "No sensor"
