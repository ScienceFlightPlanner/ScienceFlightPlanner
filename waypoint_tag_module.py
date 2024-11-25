from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QInputDialog
from qgis.core import QgsWkbTypes, QgsField, QgsFieldConstraints
from qgis.gui import QgisInterface


from .utils import LayerUtils

class WaypointTagModule:
    tags = ["Fly-by",
            "Fly-over",
            "RH 180",
            "RH 270",
            "LH 180",
            "LH 270",
            "Custom tag"]

    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def tag(self, tag):
        selected_layer = self.layer_utils.get_valid_selected_layer(
            [QgsWkbTypes.GeometryType.PointGeometry]
        )
        if selected_layer is None:
            return

        selected_features = selected_layer.getSelectedFeatures()
        selected_layer.startEditing()
        selected_layer.beginEditCommand("Reverse Waypoints")
        print(selected_layer.fields())
        if selected_layer.fields().indexFromName("tag") == -1:
            constraint = QgsFieldConstraints()
            constraint.setConstraintExpression(f'{len(tag)} <= 25', "length <= 25")
            new_field = QgsField("tag", QVariant.String)
            new_field.setConstraints(constraint)
            added = selected_layer.dataProvider().addAttributes([new_field])
            if added:
                selected_layer.updateFields()

        #selected_points = [f.geometry().asPoint() for f in selected_features]
        for f in selected_features:
            #f.attributes()
            print(f.attributes())
            print(f.fields())
            f.setAttribute("tag", tag)
            print(f.attributes())
            print(f.fields())
            selected_layer.updateFeature(f)
        selected_layer.endEditCommand()
        # update layer and commit changes
        selected_layer.updateExtents()
        selected_layer.commitChanges()
        selected_layer.reload()
        print(tag)

    def new_tag(self, parent):
        text, _ = QInputDialog.getText(parent, "Custom tag", "Enter name for custom tag:")
        print("entered text: "+text)
        self.tag(text)