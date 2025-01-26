from qgis.core import (
    Qgis,
    QgsGeometry,
    QgsVectorLayer,
    QgsMapLayer,
    QgsProject,
    QgsVectorLayerUtils,
    QgsWkbTypes,
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QMessageBox

from .constants import QGIS_FIELD_NAME_ID
from .utils import LayerUtils


class WaypointReversalModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def reverse_waypoints_action(self) -> None:
        """Reverses the Waypoints of the selected Layer"""
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [
                QgsWkbTypes.GeometryType.PointGeometry,
                QgsWkbTypes.GeometryType.LineGeometry,
            ]
        )
        if not selected_layer:
            return
        # reverse waypoints
        is_reserved = self._reverse_waypoints_for_layer(selected_layer)
        # sort features permanently according to reversal order
        if is_reserved:
            self._sort_layer_by_field_permanently(
                selected_layer, QGIS_FIELD_NAME_ID
            )
            QMessageBox.information(
                self.iface.mainWindow(),
                "Reversal was successful!",
                "Reversal of waypoints in current layer was successful!",
                QMessageBox.Ok,
            )

    def _reverse_waypoints_for_layer(self, layer: QgsMapLayer) -> bool:
        """Reverses the Waypoints of the given Layer"""
        field = self.layer_utils.get_id_field_name_for_layer(layer)
        if not field:
            return False
        features = list(layer.getFeatures()).copy()
        if len(features) == 0:
            self.iface.messageBar().pushMessage(
                "There are no Features in the currently selected Layer",
                level=Qgis.Info,
                duration=4,
            )
            return False
        if (
            len(features) == 1
            and layer.geometryType() == QgsWkbTypes.GeometryType.PointGeometry
        ):
            self.iface.messageBar().pushMessage(
                "There is only one Point Feature in the currently selected Layer",
                level=Qgis.Info,
                duration=4,
            )
            return False
        (
            attrs_for_reversal,
            not_reverse_indices,
        ) = self.layer_utils.get_id_attr_lst_for_layer(layer)
        if not attrs_for_reversal:
            return False
        # get index order for current ordering of waypoints
        indices = [
            i
            for _, i in sorted(
                zip(attrs_for_reversal, list(range(len(attrs_for_reversal))))
            )
        ]
        # get index order of reversed ordering of waypoints
        indices_reversed = indices[::-1] if not not_reverse_indices else indices
        layer.startEditing()
        layer.beginEditCommand("Reverse Waypoints")
        # update feature field and geometry according to reversed ordering
        for idx, idx_reversed in zip(indices, indices_reversed):
            feature = features[idx]
            geom = feature.geometry()
            new_geom = self._reverse_geometry(geom)
            feature.setGeometry(new_geom)
            feature[field] = attrs_for_reversal[idx_reversed]
            layer.updateFeature(feature)
        layer.endEditCommand()
        # update layer and commit changes
        layer.updateExtents()
        layer.commitChanges()
        layer.reload()
        return True

    def _reverse_geometry(self, geom: QgsGeometry) -> QgsGeometry:
        """Reverses the ordering of point of a given geometry assuming given type is either PointGeometry or LineGeometry"""
        single_type = QgsWkbTypes.isSingleType(geom.wkbType())
        # handle single type geometry
        if single_type:
            if geom.type() == QgsWkbTypes.GeometryType.PointGeometry:
                point = geom.asPoint()
                return QgsGeometry.fromPointXY(point)
            else:
                # reverse line
                reversed_polyline = geom.asPolyLine()[::-1]
                return QgsGeometry.fromPolylineXY(reversed_polyline)
        # handle multi type geometry
        else:
            if geom.type() == QgsWkbTypes.GeometryType.PointGeometry:
                # reverse multi point
                reversed_multi_point = geom.asMultiPoint()[::-1]
                return QgsGeometry.fromMultiPointXY(reversed_multi_point)
            else:
                # reverse multi line
                reversed_multi_polyline = [
                    part[::-1] for part in geom.asMultiPolyline()[::-1]
                ]
                return QgsGeometry.fromMultiPolylineXY(reversed_multi_polyline)

    def _sort_layer_by_field_permanently(
        self, layer: QgsVectorLayer, field_name: str
    ) -> None:
        """Sort currently selected layer by given field in ascending order permanently"""
        project = QgsProject.instance()
        features = list(layer.getFeatures())
        # get feature ids and attribute values
        feature_ids = []
        attr_values = []
        if len(features) == 0:
            self.iface.messageBar().pushMessage(
                "There are no Features in the currently selected Layer",
                level=Qgis.Info,
                duration=4,
            )
            return
        for feature in features:
            feature_ids.append(feature.id())
            attr_values.append(feature[field_name])
        # sort features according to attribute values in ascending order
        indices = [
            i for _, i in sorted(zip(attr_values, list(range(len(attr_values)))))
        ]
        features = [features[i] for i in indices]
        # duplicate all features in correct order
        layer.startEditing()
        layer.beginEditCommand("Sort Waypoints")
        for feature in features:
            QgsVectorLayerUtils.duplicateFeature(layer, feature, project)
        # delete old features
        layer.deleteFeatures(feature_ids)
        layer.endEditCommand()
        # update layer and commit changes
        layer.updateExtents()
        layer.commitChanges()
        layer.reload()
