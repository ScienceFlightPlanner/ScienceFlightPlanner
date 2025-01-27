import os
import subprocess
import sys
from typing import List, Tuple, Union, cast

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCoordinateTransformContext,
    QgsExpressionContextScope,
    QgsExpressionContextUtils,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsMapLayer,
    QgsPointXY,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import Qt, QVariant
from qgis.PyQt.QtWidgets import QCheckBox, QFileDialog, QMessageBox

from .constants import QGIS_FIELD_NAME_ID, PLUGIN_NAME

class LayerUtils:
    iface: QgisInterface

    def __init__(self, iface: QgisInterface) -> None:
        self.iface = iface
        self.proj = QgsProject.instance()

    def get_valid_selected_layer(
        self,
        accepted_types: List[QgsWkbTypes.GeometryType],
        is_id_attribute_required: bool = False,
        display_error_messages: bool = True,
    ) -> Union[QgsVectorLayer, None]:
        """Get the current selected layer, if no vector layer/multiple layers selected or type of selected layer not
        given in parameter lst a warning is printed and None is returned"""
        selected_layers = self.iface.layerTreeView().selectedLayers()
        # check that only one layer is selected
        if len(selected_layers) != 1:
            if display_error_messages:
                self.iface.messageBar().pushMessage(
                    "Please select exactly one layer", level=Qgis.Warning, duration=4
                )
            return

        selected_layer = selected_layers[0]
        # check that the layer is a VectorLayer
        if selected_layer.type() != QgsMapLayer.VectorLayer:
            if display_error_messages:
                self.iface.messageBar().pushMessage(
                    "Please select a vector layer", level=Qgis.Warning, duration=4
                )
            return
        else:
            selected_layer = cast(QgsVectorLayer, selected_layer)

        if selected_layer.geometryType() not in accepted_types:
            # get error string given invalid type
            accepted_type_str = ", ".join(
                map(get_geometry_type_as_string, accepted_types)
            )
            if display_error_messages:
                error_str = (
                    f"Selected layer of type {get_geometry_type_as_string(selected_layer.geometryType())}"
                    f" but required to be of type {accepted_type_str}"
                )
                self.iface.messageBar().pushMessage(
                    error_str, level=Qgis.Warning, duration=4
                )
            return

        if is_id_attribute_required:
            if self.get_id_attr_lst_for_layer(selected_layer) is None:
                return

        return selected_layer

    def get_id_attr_lst_for_layer(
        self, layer: QgsMapLayer.VectorLayer
    ) -> Union[Tuple[List[object], bool], Tuple[None, None]]:
        """Get values of field for given features, if resulting list contains None or duplicates a message is printed
        and None returned"""
        field_name = self.get_id_field_name_for_layer(layer)
        if not field_name:
            return None, None
        features = list(layer.getFeatures())
        var_name = "sfp_total_number_waypoints"
        attributes = [feature[field_name] for feature in features]
        reduction = False
        if QgsExpressionContextScope.hasVariable(
            QgsExpressionContextUtils.layerScope(layer), var_name
        ):
            total_number_wp = QgsExpressionContextScope.variable(
                QgsExpressionContextUtils.layerScope(layer), var_name
            )
            attributes = [
                int(total_number_wp) - feature[field_name] + 1 for feature in features
            ]
            reduction = True

        # check for None
        if None in attributes:
            self.iface.messageBar().pushMessage(
                f"Please select vector layer where all features have an assigned '{field_name}'",
                level=Qgis.Warning,
                duration=4,
            )
            return None, None
        # check whether list of values contains duplicates
        if len(set(attributes)) < len(attributes):
            self.iface.messageBar().pushMessage(
                f"Please select vector layer where all features have a unique '{field_name}'",
                level=Qgis.Warning,
                duration=4,
            )
            return None, None
        return attributes, reduction

    def get_id_field_name_for_layer(self, layer: QgsMapLayer) -> Union[str, None]:
        """Get name of field used for reversing features of a given layer, if given feature does not have a feature
        like id a message is printed and None is returned"""
        fields = layer.fields()
        index = fields.lookupField(QGIS_FIELD_NAME_ID)
        # check whether field like id is in list of fields of given layer
        if index < 0:
            self.iface.messageBar().pushMessage(
                f"Please select a vector layer that has field '{QGIS_FIELD_NAME_ID}'",
                level=Qgis.Warning,
                duration=4,
            )
            return
        field_name = fields.at(index).name()
        return field_name

    def validate_file_path(self, file_path, file_type):
        if not file_path.lower().endswith(file_type):
            file_path += file_type

        return file_path

    def check_if_path_exists(self, file_path):
        if os.path.exists(file_path):
            self.iface.messageBar().pushMessage(
                "Please select a file path that does not already exist",
                level=Qgis.Warning,
                duration=4,
            )
            return True
        return False

    def create_file_dialog(
            self,
            dialog_title,
            path_of_current_layer,
            filter, path_suffix
    ):
        suggested_path, _ = os.path.splitext(path_of_current_layer)
        suggested_path += path_suffix
        file_path, _ = QFileDialog.getSaveFileName(
            self.iface.mainWindow(), dialog_title, suggested_path, filter
        )
        return file_path

    def get_shp_file_path(
            self,
            dialog_title: str,
            path_of_current_layer: str,
            path_suffix: str
    ) -> Union[None, str]:

        filter = "ESRI Shapefile (*.shp *.SHP)"
        file_path = self.create_file_dialog(
            dialog_title, path_of_current_layer, filter, path_suffix
        )

        if not file_path:
            return

        file_path = self.validate_file_path(file_path, ".shp")

        if self.check_if_path_exists(file_path):
            return

        return file_path

    def generate_shp_file(
        self,
        current_layer_path: str,
        path_suffix: str,
        waypoints: List[QgsPointXY],
        waypoint_ids: List[int],
        source_crs: QgsCoordinateReferenceSystem,
    ) -> Union[None, Tuple[QgsVectorFileWriter, QgsMapLayer]]:
        """Generates an SHP-File that contains the given waypoints and saves it at the given path"""
        dialog_title = "Save Waypoint Layer As"
        # select file path of shp-file
        file_path = self.get_shp_file_path(dialog_title, current_layer_path, path_suffix)

        if not file_path:
            return

        # transform waypoints in correct coordinate reference system
        destination_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        crs_translator = QgsCoordinateTransform(
            source_crs, destination_crs, QgsProject.instance()
        )

        for index in range(len(waypoints)):
            waypoints[index] = crs_translator.transform(waypoints[index])

        fields = QgsFields()
        fields.append(QgsField(QGIS_FIELD_NAME_ID, QVariant.Int))

        # create the File Writer
        writer = self.create_vector_file_write(
            file_path,
            fields,
            QgsWkbTypes.Point,
            destination_crs,
        )

        # add a feature for each waypoint
        for index, point in zip(waypoint_ids, waypoints):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(point))
            feature.setAttributes([index])
            writer.addFeature(feature)

        # add vector as layer
        layer = self.iface.addVectorLayer(file_path, "", "ogr")

        layer.reload()
        return writer, layer

    def create_vector_file_write(
        self,
        file_name: str,
        fields: QgsFields,
        geometry_type: QgsWkbTypes,
        crs: QgsCoordinateReferenceSystem,
    ) -> QgsVectorFileWriter:
        """Creates a QGSVectorFileWriter with the given attributes"""
        try:
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.fileEncoding = "UTF-8"
            options.driverName = "ESRI Shapefile"

            return QgsVectorFileWriter.create(
                file_name,
                fields,
                geometry_type,
                crs,
                QgsCoordinateTransformContext(),
                options,
            )
        except NameError:
            # Needed for QGIS versions older than 3.10.3
            return QgsVectorFileWriter(
                file_name,
                "UTF-8",
                fields,
                QgsWkbTypes.Point,
                crs,
                "ESRI Shapefile",
            )

    def get_selected_feature_from_layer(self, layer: QgsMapLayer):
        """Returns the selected feature of the given layer or the only feature if only one feature is present. If no or multiple features are selected an according warning is thrown."""
        features = list(layer.getFeatures())
        if len(features) == 1:
            feature = features[0]
        elif len(features) == 0:
            self.iface.messageBar().pushMessage(
                "There are no features in the currently selected layer",
                level=Qgis.Info,
                duration=4,
            )
            return None
        else:
            selected_features = layer.selectedFeatures()
            if len(selected_features) != 1:
                settings_txt = "show_multiple_selection_info"
                txt = 'Multiple Features in Layer! \n\nPlease select exactly one Feature: \n\nSelection Tools for Features are available \n\n1) in the QGIS "Selection Toolbar"\n2) via "Edit ▶ Select" \n\n'

                if not show_checkable_info_message_box(
                    settings_txt, txt, QgsProject.instance()
                ):
                    self.iface.messageBar().pushMessage(
                        "Multiple features in the currently selected layer and no/multiple selected. Select exactly one feature.",
                        level=Qgis.Info,
                        duration=4,
                    )
                return None
            feature = selected_features[0]
        return feature

    def add_field_to_layer(
            self, layer, qgis_field_name, field_type, default_field_value, message
    ) -> bool:
        """Adds field with specified name and type to given layer depending on user prompt"""
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            f"Add Field {qgis_field_name} to Layer {layer.name()}?",
            f"Add Field '{qgis_field_name}' to Layer {layer.name()}?\n"
            f"{message}",
            QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.No:
            return False

        new_field = QgsField(qgis_field_name, field_type)
        added = layer.dataProvider().addAttributes([new_field])
        if added:
            layer.updateFields()

        if default_field_value is not None:
            attr_map = {}
            field_id = layer.fields().indexFromName(qgis_field_name)
            for feature in layer.getFeatures():
                attr_map[feature.id()] = {field_id: default_field_value}

            layer.dataProvider().changeAttributeValues(attr_map)
            layer.updateFields()

        return added

    def delete_field_from_layer(
        self, layer: QgsMapLayer, field_name: str
    ) -> bool:
        """Deletes field with specified name from given layer depending on user prompt"""
        fields = layer.fields()
        index = fields.indexFromName(field_name)
        if index < 0:
            return False
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            f"Delete field {field_name} from layer {layer.name()}?",
            f"Delete field '{field_name}' from layer {layer.name()}?\n\n"
            f"If '{field_name}' is not deleted,\nselected points cannot be "
            f"highlighted.",
            QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply:
            deleted = layer.dataProvider().deleteAttributes([index])
            if deleted:
                layer.updateFields()
            return deleted
        else:
            return False

def get_geometry_type_from_string(geom_string: str) -> QgsWkbTypes.GeometryType:
    """Returns Geometry Type for a given string (assumes valid geometry type)"""
    types = {
        "PointGeometry": QgsWkbTypes.GeometryType.PointGeometry,
        "LineGeometry": QgsWkbTypes.GeometryType.LineGeometry,
        "PolygonGeometry": QgsWkbTypes.GeometryType.PolygonGeometry,
        "UnknownGeometry": QgsWkbTypes.GeometryType.UnknownGeometry,
        "NullGeometry": QgsWkbTypes.GeometryType.NullGeometry,
    }
    return types[geom_string]


def get_geometry_type_as_string(geom_type: QgsWkbTypes.GeometryType) -> str:
    """Return given Geometry Type as String"""
    geom_strs = {
        QgsWkbTypes.GeometryType.PointGeometry: "PointGeometry",
        QgsWkbTypes.GeometryType.LineGeometry: "LineGeometry",
        QgsWkbTypes.GeometryType.PolygonGeometry: "PolygonGeometry",
        QgsWkbTypes.GeometryType.UnknownGeometry: "UnknownGeometry",
        QgsWkbTypes.GeometryType.NullGeometry: "NullGeometry",
    }
    return geom_strs.get(geom_type, "GeometryType not found")


def show_checkable_info_message_box(
    settings_name: str, txt: str, proj: QgsProject
) -> bool:
    """Opens a MessageBox with option to disable future display of the same information"""
    show_info = proj.readBoolEntry(PLUGIN_NAME, settings_name, True)[0]
    show_info_bool = show_info if isinstance(show_info, bool) else show_info == "true"
    if show_info_bool:
        check_box = QCheckBox("Don't show this again.")
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle(PLUGIN_NAME)
        message_box.setText(txt)
        message_box.addButton(QMessageBox.Ok)
        message_box.setDefaultButton(QMessageBox.Ok)
        message_box.setCheckBox(check_box)

        message_box.exec()
        if check_box.checkState() == Qt.Checked:
            proj.writeEntryBool(PLUGIN_NAME, settings_name, False)
    return show_info

"""Methods for automatic external library installation"""
# Not needed for now as qgis already comes with the geopandas package, but may be useful later
def install_package(package_name):
    """Tries to install a library"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)
    except subprocess.CalledProcessError:
        QMessageBox.critical(None, "Fehler", f"Das Paket '{package_name}' konnte nicht installiert werden.")

def ensure_dependencies():
    """Überprüft und installiert fehlende Abhängigkeiten."""
    try:
        import geopandas
    except ImportError:
        reply = QMessageBox.question(
            None,
            "Abhängigkeiten installieren",
            "Das Paket 'geopandas' wird benötigt. Möchtest du es jetzt installieren?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            install_package("geopandas")
