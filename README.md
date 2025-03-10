# User-manual

The ScienceFlightPlanner Plugin helps in improving your workflow when planning scientific flight surveys.

The plugin consists of eight core features. Seven of them are represented with according buttons and one feature can be accessed via the selection box in the toolbar.

In addition to this help manual, you can find tutorial videos for using our plugin on our Youtube channel [ScienceFlightPlanner](https://www.youtube.com/channel/UCkSBaCW_Sohcqlh8Pu6tufg)

## Feature Overview

Feature name | Access via                                                 | Short description                                                                                                                                                                                                              | Applicable to geometry type
---|------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---
Display Flight Distance | ![](resources/icons_for_dark_mode/icon_distance.png)       | Shows the length of the current flight plan in meters.                                                                                                                                                                         | Line 
Display Flight Duration | ![](resources/icons_for_dark_mode/icon_duration.png)       | Shows the expected flight duration of the current flight plan in hours.                                                                                                                                                        | Line 
Generate Waypoints for Flight Plan | ![](resources/icons_for_dark_mode/icon_file.png)           | Generates a new shapefile which contains all waypoints (numbered from 1 to n) of the current flight plan.                                                                                                                      | Line 
Export in Garmin GTN750Xi Format | ![](resources/icons_for_dark_mode/icon_export.png)         | Generates a wpt- and a gfp-file for the Garmin GTN™ 750Xi based on the current flight plan.                                                                                                                                    | Waypoints file
Add tag to selected waypoints | ![](resources/icons_for_dark_mode/icon_tag.png)            | Adds a tag to the selected waypoints of the current flight plan.                                                                                                                                                               | Points
Mark Selected Waypoints as Significant | ![](resources/icons_for_dark_mode/icon_highlight.png)      | Marks the selected waypoints of the current flight plan as significant.                                                                                                                                                        | Points 
Generate Reduced Flight Plan from Significant Waypoints | ![](resources/icons_for_dark_mode/icon_labels.png)         | Extracts waypoints of currently selected waypoints that were previously marked as significant to a new shapefile.                                                                                                              | Points 
Reverse Waypoints | ![](resources/icons_for_dark_mode/icon_reverse.png)        | Reverses the order of current waypoints or flight plan.                                                                                                                                                                        | Line, Points 
Show Coverage | Sensor selection box in toolbar                            | When a specific sensor is chosen, the current flight plan's coverage for this specific sensor and flight altitude is computed and saved to a new shapefile.                                                                    | Line 
Compute Optimal Coverage Lines | ![](resources/icons_for_dark_mode/icon_coverage_lines.png) | Given a sensor and an area of interest are selected, optimal flight lines are computed which coverage covers the selected area.                                                                                                | Polygon 
Cut flowline | ![](resources/icons_for_dark_mode/icon_cut_flowline.png)   | Cut a flowline out of a given flowline at the selected waypoints                                                                                                                                                               | Points
Racetrack from Polygon | ![](resources/icons_for_dark_mode/icon_racetrack.png)      | Given a polygone, flight alttitude, max turning distance calculates optimal waypoints for a plane based on selected algorithm                                                                                                  | Polygon 
Create a Topography Profile | ![](resources/icons_for_dark_mode/icon_topography.png)       | Given a wpt layer, a digital elevation model (.tif), and a maximum climb rate of a plane, it generates a topography profile that highlights zones where the required climb rate exceeds the aircraft's performance. | Waypoint file 
## Detailed feature description

### Display Flight Distance

![](resources/icons_for_dark_mode/icon_distance.png)

When the above button is pressed and a line layer is selected [(FAQ)](#faq), then the length (km) of the flight plan in this layer is shown. While activated, the display of the flight distance updates in accordance to changes in the layer/feature selection [(FAQ)](#faq). If the button is pressed again, the display of the length is toggled. Whether the tool is activated, is indicated by toggling the button.

### Display Expected Flight Duration

![](resources/icons_for_dark_mode/icon_duration.png)

When the above button is pressed and a line layer is selected [(FAQ)](#faq), the expected duration (h) for flying along the flight plan in this layer is shown. While activated, the display of the flight duration updates in accordance to changes in the layer/feature selection [(FAQ)](#faq). If the button is pressed again, the display of the duration is toggled. Whether the tool is activated, is indicated by toggling the button.

The used flight speed can be set in the plugin settings [(FAQ)](#faq) with a default speed set to 200km/h.

### Generate Waypoints for Flight Plan

![](resources/icons_for_dark_mode/icon_file.png)

When the above button is pressed and a line layer is selected [(FAQ)](#faq), all waypoints of this layer\'s flight plan are extracted. A waypoint is defined as each point in the flight path where the flight changes direction.

A window will pop up in which you can set the name and location of the shp-file in which the extracted waypoints will be stored as points.

### Export in Garmin GTN750Xi Format

![](resources/icons_for_dark_mode/icon_tag.png)

When the above button is pressed, the selected flight plan file will be transformed into flight plans files compatible with the Garmin GTN750. 
After pressing the button, the selected .wpt file will be transformed into two files of following format: 
- example_user.wpt (MUST be named _user.wpt for import) 
- example_gfp.gfp

_Hint: To avoid the GTN750Xi system giving the waypoints coordinates a generic ID, first import the user.wpt file and only after this import the .gfp-file._

### Add tag to selected waypoints

![](resources/icons_for_dark_mode/icon_export.png) 

After selecting a waypoint or multiple waypoints [(FAQ)](#faq) and pressing this button, a label is added to the point.

You can choose from the following predefined tags:  
- **FLYOVER**  
- **FLYBY**  
- **RH180** – Right Hand 180°  
- **RH270** – Right Hand 270°  
- **LH-180** – Left Hand 180°  
- **LH-270** – Left Hand 270°  

Additionally, you can create a custom tag. **Note**: Custom tags must **not exceed 10 characters** in length.

After adding a tag, select the corresponding waypoint to see the tag displayed in the **status bar** at the bottom of the screen.  

To view all waypoints and their associated tags:  
   1. Select the **waypoint layer**.  
   2. Open the **Attribute Table** (right-click → “Open Attribute Table”).

### Mark Selected Waypoints as Significant

![](resources/icons_for_dark_mode/icon_highlight.png)

When the above button is pressed and some waypoints are selected [(FAQ)](#faq) they are marked as significant. This means a field \"sig\" is added to the attribute table of the points which you have to confirm.

Afterwards each significant point is marked with a little star.

### Generate Reduced Flight Plan from Significant Waypoints

![](resources/icons_for_dark_mode/icon_labels.png)

When the above button is pressed and waypoints in the current layer were previously marked as significant, i.e. the flight plan layer has the field \"sig\", as generated by [\"Mark selected Waypoints as Significant\"](#mark_sig), the waypoints chosen to be significant will be saved in a new shp-file. The points in the new shp-file have ids according to their position in the original flight plan.

In the following pop-up you can then select location and name of the new file.

### Reverse Waypoints

![](resources/icons_for_dark_mode/icon_reverse.png)

When the above button is pressed and a line layer or a layer containing waypoints is selected [(FAQ)](#faq) and the features have the field id, the order of the waypoints or the layer\'s flight plan is reversed.

_Example: If the starting point had number 1 and the end point number 30 and the waypoints are reversed, the original starting point will then be number 30 and the original end point number 1.__

### Show coverage

When a line layer is selected [(FAQ)](#faq) and a sensor in the sensor selection box of the plugin toolbar is selected, a new shp-file will be created containing the area which is covered by the flight plan in the layer for a specific flight altitude and the selected sensor.

Given a coverage shp-file has been created for the current flight plan and sensor, changing the flight altitude or the sensor settings results in an update of the corresponding coverage shp-file. The flight altitude can be changed in the flight altitude SpinBox in the plugin\'s toolbar. Sensors can be added, deleted or changed in the plugin settings
[(FAQ)](#faq).

Before this feature can be used, it is necessary to set the CRS used for coverage computations in the plugin settings. The CRS should be compatible with the region of the QGIS project.

### Compute Optimal Coverage Lines

![](resources/icons_for_dark_mode/icon_coverage_lines.png)

When the above button is pressed, optimal flight lines are computed given a sensor and a polygon, representing an area of interest, are selected. These lines can be used as a template for a flight plan over the area of interest which for the selected sensor has some amount of overlap with as few turns as possible.

The flight altitude can be changed in the flight altitude SpinBox in the toolbar and sensors can be added, deleted or changed in the plugin settings [(FAQ)](#faq).

The amount of overlap which is considered when creating the optimal flight lines can also be changed in the plugin settings. Overlap means how much adjacent coverage segments overlap each other (see example below).

0% overlap

![](./resources/user_manual/overlap_0_percent.png)

50% overlap

![](./resources/user_manual/overlap_50_percent.png)

Additionally, it is possible to use two different settings for the line computations. The default setting, which we strongly suggest to use, is called \"optimal\". In this case the lines are optimal w.r.t. the criteria described above. Choosing \"90° rotated\" means that the lines are 90° rotated from the optimal orientation. Therefore, they are no longer optimal but depending on the flight plan and use case this might still be useful.

In order to use this feature for the first time it is necessary to set the CRS used for coverage computations in the plugin settings. The CRS should be compatible with the region of the QGIS project.
### Convert Polygon to Racetrack

![Topography Profile Icon](resources/icons_for_dark_mode/icon_racetrack.png) 

The Racetrack feature calculates optimal waypoints for a plane when the designated button is pressed. These waypoints are determined based on the selected sensor, polygon-layer representing the area of interest, and flight altitude. Note that the selected polygon layer must contain only one feature.

Key Features of Waypoints

**Fly-over Tag:** Each waypoint is assigned a fly-over tag by default.  
**Unique IDs:** Waypoints are assigned unique IDs based on the selected algorithm, indicating the order in which they need to be flown over.  

The algorithms are designed to optimize the flight path when flying over a grid. You can choose between two algorithms:

**Meander Algorithm**

The plane flies over `k` waypoints repeatedly until it reaches the end of the grid.  
It then moves back by 1 waypoint.  
The plane continues flying `k` waypoints in the opposite direction, repeating the process until the grid is fully covered.

**Racetrack Algorithm**

The plane flies over the first `k` waypoints (determined by the maximum turning distance).  
It then flies back over `k-1` waypoints, reversing direction.  
This process repeats until the entire area is covered.

**Suggested Naming for Output Files**

The generated output files include the maximum turning distance in their filenames to make them easily identifiable.


### Create a Topography Profile

![Topography Profile Icon](resources/icons_for_dark_mode/icon_topography.png)

Given a wpt layer, a digital elevation model (.tif), and a maximum climb rate of a plane, it generates a topography profile that highlights zones where the required climb rate exceeds the aircraft's performance.

**Graph Generation**

When a waypoint layer is selected and the topography button is pressed, select a DEM file. The feature will then generate a graph in a dock window. The top of this window shows the waypoint numbers, which correspond directly to the points on the selected flight path. 

**Graph Interaction and Navigation**

The dock window offers several interactive actions with the graph:

- **Zoom In:** Increase the magnification to view a detailed section of the graph.
- **Zoom Out:** Decrease the magnification to obtain a broader overview.
- **Full Zoom Out:** Use the button located in the bottom left corner to reset the view and display the complete topography profile. 
- **Drag Graph:** Click and hold the graph to drag and navigate through different sections of the elevation profile.
- **Show Waypoints:** Use the button in the bottom left corner to display vertical lines that indicate each waypoint on the graph. 
**Critical Zones Indicator**

The profile graph visually highlights critical zones in red - areas where the climb rate needed to maintain the current altitude above the terrain exceeds the aircraft's available climb rate. The critical zones can be seen ob both the graph and the layer. An aircraft's climb rate can be entered in the 'Maximum climb rate in feet/min' field in the toolbar. 

## FAQ

#### What does it mean that some feature has to be selected?

This means, that either the feature is the only feature in the current layer or the feature is selected with the QGIS selection tool which can be found in the standard toolbar (\"Selection Toolbar\") or via \"Edit ▶Select\".

#### How can I select multiple features?

Especially when you want to mark multiple points as significant it is useful to select multiple points. To select multiple points, press and hold the \"CRTL\" key (on Mac: \"Command\" key) and click on the features you want to select.

#### Where can the plugin settings be found?

The plugin setting can be found under: \"Settings ▶ Options\... ▶ ScienceFlightPlanner\".\ There it is possible to change the flight speed, the CRS used for computing sensor coverage, the setting used for computing overlap and to add, delete or change sensors.

#### I\'ve activated the flight duration/distance display, how is it updated?

When the flight duration/distance display is activated (indicated by a toggled button of the corresponding feature) the distance/duration is updated in accordance to the current layer/feature selection. This means that when for example changing the layer to a different line layer, the distance/duration is updated to match the new layer. If the layer contains multiple features, it is required to explicitly select one feature for which the distance/duration is to be shown. Similarly, as for a new layer selection, a new feature selection within the current layer results in an update of the distance/duration. When a layer of a geometry other than line is selected, the display is toggled until a layer of type line is selected again.

## Acknowledgments

This plugin makes use of [**garmin_fpl**](https://github.com/awi-response/garmin_fpl):

Rettelbach, T., Döpper, V., & Nitze, I. (2024). garmin_fpl: Creation and conversion scripts for Garmin flightplans for scientific flight campaigns [Computer software]