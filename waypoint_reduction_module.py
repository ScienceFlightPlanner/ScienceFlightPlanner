from typing import Dict, List, Tuple, Union

from qgis.core import (
    Qgis,
    QgsExpressionContextUtils,
    QgsFeature,
    QgsMapLayer,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsProject,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes,
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QVariant

from .constants import (
    QGIS_FIELD_NAME_ID,
    QGIS_FIELD_NAME_SIG,
    DEFAULT_PUSH_MESSAGE_DURATION
)
from .utils import LayerUtils, show_checkable_info_message_box


class WaypointReductionModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

        # labeling of waypoints marked as significant
        self.iface.layerTreeView().currentLayerChanged.connect(
            self.enable_labeling_sig_filtering
        )
        self.enable_labeling_sig_filtering(self.iface.activeLayer())

    def close(self):
        self.iface.layerTreeView().currentLayerChanged.disconnect(
            self.enable_labeling_sig_filtering
        )

    def highlight_selected_waypoints(self) -> None:
        """Marks selected points of currently selected layer. If feature marked as significant is part of selection
        it is marked as insignificant.If field does not exist user is prompted whether he wants to add the field.
        Only if field is added selected points are marked"""
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry], is_id_attribute_required=True
        )
        if not selected_layer:
            return

        features = list(selected_layer.getFeatures())
        # notify user if no changes can be made due to layer configuration
        if len(features) == 0:
            self.iface.messageBar().pushMessage(
                "There are no features in the currently selected layer",
                level=Qgis.Info,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        selected_features = list(selected_layer.getSelectedFeatures())
        # notify user if no changes cannot be made due to missing feature selection
        if len(selected_features) == 0:
            settings_name = "show_selection_info"
            txt = ('No features were marked significant! \n\nThere are no features selected in the currently selected '
                   'layer: \n\nSelection Tools for Features are available \n\n1) in the QGIS "Selection Toolbar"\n2) '
                   'via "Edit ▶ Select. \n\n To select multiple points, press and hold the \"CTRL\" key (on Mac: '
                   '\"Command\" key) and click on the features you want to select.\n\n')

            if not show_checkable_info_message_box(settings_name, txt, QgsProject.instance()):
                self.iface.messageBar().pushMessage(
                    "No features selected in currently selected layer. Please select one/multiple features.",
                    level=Qgis.Info,
                    duration=DEFAULT_PUSH_MESSAGE_DURATION,
                )
            return

        # check that all features are of single geometry type
        multi_type_features = [
            feature
            for feature in selected_layer.getFeatures()
            if not QgsWkbTypes.isSingleType(feature.geometry().wkbType())
        ]
        if len(multi_type_features) != 0:
            self.iface.messageBar().pushMessage(
                "Please select layer where all features are of single geometry type.",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return

        # store ids of features that were selected before highlighting
        selected_ids = [feature.id() for feature in selected_features]

        # enforce a valid significance filtering field in layer
        valid_before, valid_now = self._enforce_valid_significance_filtering_field(
            selected_layer
        )
        if not valid_now:
            return
        # retrieve features and selected features
        features = list(selected_layer.getFeatures())
        selected_features = [
            feature for feature in features if feature.id() in selected_ids
        ]
        # highlight features
        new_sig_dic = self._highlight_features(
            selected_layer, features, selected_features
        )

        selected_layer.reload()
        selected_layer.select(selected_ids)
        if not valid_before:
            self.add_sig_filtering_label(selected_layer)

    def generate_significant_waypoints_shp_file_action(self) -> None:
        """Generates an SHP-file that contains a reduced number waypoints of the selected SHP-File containing the
        waypoints and a significance highlighting"""
        # retrieve selected Layer and check for validity
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry], is_id_attribute_required=True
        )
        if not selected_layer:
            return
        # get reduced waypoints
        waypoints, waypoint_ids = self.get_reduced_waypoints_of_layer(selected_layer)
        if not waypoints:
            return

        current_layer_path = selected_layer.dataProvider().dataSourceUri()
        # generate shp-file
        writer_layer_tuple = self.layer_utils.generate_shp_file(
            current_layer_path, "_reduced", waypoints, waypoint_ids, selected_layer.crs()
        )
        if writer_layer_tuple is None:
            return

        _, layer = writer_layer_tuple

        if not layer:
            return
        QgsExpressionContextUtils.setLayerVariable(
            layer, "sfp_total_number_waypoints", len(list(selected_layer.getFeatures()))
        )
        layer.reload()
        # create labeling for new layer
        self.label_layer_features(layer, QGIS_FIELD_NAME_ID)

    def _enforce_valid_significance_filtering_field(
        self, layer: QgsMapLayer
    ) -> Tuple[bool, bool]:
        """ensure that layer has a valid significance field; if enforcing validity not possible print message"""
        # get index for field with significance filtering
        fields = layer.fields()
        index = fields.indexFromName(QGIS_FIELD_NAME_SIG)
        valid = True

        # if field exists in layer check for validity
        if index >= 0:
            valid = self._check_significance_field(layer)
            # prompt user to delete field if not valid
            if not valid:
                deleted = self.layer_utils.delete_field_from_layer(
                    layer,
                    QGIS_FIELD_NAME_SIG,
                    f"If '{QGIS_FIELD_NAME_SIG}' is not deleted,\nselected points cannot be highlighted."
                )
                if not deleted:
                    self.iface.messageBar().pushMessage(
                        "Features could not be highlighted since field for significance filtering is invalid but could "
                        "not be deleted from layer",
                        level=Qgis.Warning,
                        duration=DEFAULT_PUSH_MESSAGE_DURATION,
                    )
                    return valid, False
                fields = layer.fields()
                index = fields.indexFromName(QGIS_FIELD_NAME_SIG)
                layer.updateExtents()
                layer.reload()

        # prompt user whether they want to add the field used for significance filtering
        # if user selects 'yes' field is added to currently selected layer
        if index < 0:
            valid = False
            added = self.layer_utils.add_field_to_layer(
                layer,
                QGIS_FIELD_NAME_SIG,
                QVariant.Bool,
                None,
                f"If '{QGIS_FIELD_NAME_SIG}' is not added ,\nselected Points cannot be highlighted."
            )
            if not added:
                self.iface.messageBar().pushMessage(
                    f"Features could not be highlighted since field {QGIS_FIELD_NAME_SIG} could not be added to layer",
                    level=Qgis.Warning,
                    duration=DEFAULT_PUSH_MESSAGE_DURATION,
                )
                return valid, False
            layer.updateExtents()
            layer.reload()

        return valid, True

    def _highlight_features(
        self,
        layer: QgsMapLayer,
        features: List[QgsFeature],
        selected_features: List[QgsFeature],
    ) -> Dict[bool, List[int]]:
        """Highlight Features as insignificant/significant. Assumes that field for significance filtering exists in
        selected layer"""
        index = layer.fields().indexFromName(QGIS_FIELD_NAME_SIG)
        new_significance_dic = {True: [], False: []}
        # set field used for significance filtering to being editable
        self.set_read_only_config_for_field(layer, QGIS_FIELD_NAME_SIG, False)
        layer.startEditing()
        layer.beginEditCommand("Highlight Waypoints")
        for feature in features:
            attr = feature[QGIS_FIELD_NAME_SIG]
            # check if attribute value has not been set if so set to False
            if type(attr) is QVariant and attr.isNull():
                attr = False
            # if feature selected change attribute value
            if feature in selected_features:
                attr = not attr
                new_significance_dic[attr].append(
                    feature[QGIS_FIELD_NAME_ID]
                )
            layer.changeAttributeValue(feature.id(), index, attr)
        # set field used for significance filtering to not being editable
        self.set_read_only_config_for_field(layer, QGIS_FIELD_NAME_SIG, True)
        # update layer and commit changes
        layer.endEditCommand()
        layer.updateExtents()
        layer.commitChanges()
        layer.reload()
        return new_significance_dic

    def set_read_only_config_for_field(
        self, layer: QgsMapLayer, field_name: str, read_only: bool
    ) -> None:
        """Control whether given field of currently selected layer can be edited"""
        fields = layer.fields()
        field_idx = fields.indexOf(field_name)
        form_config = layer.editFormConfig()
        form_config.setReadOnly(field_idx, read_only)
        layer.setEditFormConfig(form_config)

    def get_reduced_waypoints_of_layer(
        self, layer: QgsMapLayer
    ) -> Tuple[List[QgsPointXY], List[int]]:
        """Retrieves the Reduced Waypoints of a PointGeometry as marked by the corresponding field, if currently
        selected layer does not contain the field used for significance filtering a warning is printed and an empty
        list returned"""
        fields = layer.fields()
        # selected layer does not have attribute used for significance filtering
        if fields.indexFromName(QGIS_FIELD_NAME_SIG) < 0:
            self.iface.messageBar().pushMessage(
                "Please select a vector layer compatible for significance filtering",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return [], []
        # reduce waypoints
        features = list(layer.getFeatures())
        reduced_features = [feature for feature in features if feature[QGIS_FIELD_NAME_SIG]]
        waypoints = [feature.geometry().asPoint() for feature in reduced_features]
        waypoint_ids = [feature[QGIS_FIELD_NAME_ID] for feature in reduced_features]

        if len(waypoints) == 0:
            self.iface.messageBar().pushMessage(
                "Layer does not have any waypoints marked as significant",
                level=Qgis.Warning,
                duration=DEFAULT_PUSH_MESSAGE_DURATION,
            )
            return [], []

        return waypoints, waypoint_ids

    def add_sig_filtering_label(self, layer: QgsMapLayer) -> None:
        """add labeling expression from layer used for significance filtering"""

        # if significance filtering does not apply to layer nothing has to be done
        if not self._check_validity_of_layer_for_significance_filtering(layer):
            return

        label = layer.labeling()
        expr = self.get_sig_label_expression()

        # if layer has already some labeling enabled add significance labeling to it
        if label is not None:
            settings = label.settings()
            field_name = settings.fieldName
            if expr not in field_name and layer.labelsEnabled():
                expr = f"{expr}||{field_name}"

        self.label_layer_features(layer, QGIS_FIELD_NAME_SIG, expr)

    def label_layer_features(
        self,
        layer: QgsMapLayer,
        field_name: str,
        expression: Union[str, None] = None,
    ) -> None:
        """label layer according to a new specified labeling expression"""

        is_expression = expression is not None
        label_expression = expression if is_expression else f"{field_name}"

        # if labeling exists use the settings and placing defined for those
        if layer.labeling() is not None:
            layer_settings = layer.labeling().settings()
        # if labeling does not exist define new settings and placing
        else:
            layer_settings = QgsPalLayerSettings()
            text_format = QgsTextFormat()

            # placing
            layer_settings.xOffset = 4.5
            try:
                layer_settings.placement = 1
            except (NameError, TypeError):
                layer_settings.placement = QgsPalLayerSettings.OverPoint
                layer_settings.offsetType = QgsPalLayerSettings.FromPoint

            # buffer
            buffer_settings = QgsTextBufferSettings()
            buffer_settings.setEnabled(True)

            text_format.setBuffer(buffer_settings)
            layer_settings.setFormat(text_format)

        # set new field name
        layer_settings.fieldName = label_expression

        layer_settings.isExpression = is_expression

        # enable labeling
        layer.setLabelsEnabled(True)
        try:
            layer_settings.drawLabels = True
        except NameError:
            pass
        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        layer.setLabeling(layer_settings)
        try:
            layer_settings.drawLabels = True
        except NameError:
            pass
        layer.triggerRepaint()

    def _check_validity_of_layer_for_significance_filtering(
        self, layer: QgsMapLayer
    ) -> bool:
        """check whether layer is compatible for significance labeling"""
        if (
            not layer
            or layer.type() != QgsMapLayer.VectorLayer
            or layer.geometryType() != QgsWkbTypes.GeometryType.PointGeometry
        ):
            return False

        layer_fields = layer.fields()
        layer_field_names = list(map(lambda field: field.name(), layer_fields))
        if QGIS_FIELD_NAME_SIG not in layer_field_names:
            return False
        return self._check_significance_field(layer)

    def get_sig_label_expression(self):
        """get label expression used for the currently selected layer to display which features are marked
        significant"""
        return f"if (\"sig\"!=0,'★  ','')"

    def enable_labeling_sig_filtering(self, current_layer: QgsMapLayer):
        all_layers_proj = list(QgsProject.instance().mapLayers().values())
        selected_layers = self.iface.layerTreeView().selectedLayers()

        # only enable labeling if exactly one layer is selected
        if len(selected_layers) != 1:
            return

        # remove significance labeling from layers not currently selected
        for layer in all_layers_proj:
            # add significance labeling to currently selected layer
            if layer == current_layer:
                self.add_sig_filtering_label(current_layer)
            else:
                self.remove_sig_filtering_label(layer)

    def remove_sig_filtering_label(self, layer: QgsMapLayer) -> None:
        """remove labeling expression from layer used for significance filtering"""
        # if significance filtering does not apply to layer nothing has to be done
        if not self._check_validity_of_layer_for_significance_filtering(layer):
            return

        expr = self.get_sig_label_expression()
        label = layer.labeling()

        # if no labeling exists for layer nothing has to be done
        if label is None:
            return

        settings = label.settings()
        field_name = str(settings.fieldName)

        # case labeling expression consists only of significance labeling
        if expr == field_name:
            field_name = ""

        # case labeling expression contains other labeling expressions as well
        # assumption that significance filtering only applied to automatically by union
        while expr in field_name:
            if expr + "||" in field_name:
                current_expr = expr + "||"
            elif "||" + expr in field_name:
                current_expr = "||" + expr
            else:
                current_expr = expr
            field_name = field_name.replace(current_expr, "")
        settings.fieldName = field_name

        # if no label exists -> disable labeling
        if field_name == "":
            layer.setLabelsEnabled(False)

        # update labeling settings
        settings = QgsVectorLayerSimpleLabeling(settings)
        layer.setLabeling(settings)
        layer.triggerRepaint()

    def _check_significance_field(self, layer: QgsMapLayer) -> bool:
        """check whether field for significance filtering is valid"""
        fields = layer.fields()
        index = fields.indexFromName(QGIS_FIELD_NAME_SIG)
        field = fields.at(index)
        if field.type() != QVariant.Int:
            return False
        attrs = [feature[QGIS_FIELD_NAME_SIG] for feature in layer.getFeatures()]
        invalid_attrs = [
            attr for attr in attrs if attr not in [None, 0, 1, True, False]
        ]
        if len(invalid_attrs) != 0:
            return False
        return True
