import csv
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QMessageBox
from qgis.core import QgsVectorLayer, QgsPoint, QgsFeature, QgsGeometry, QgsProject, QgsField, \
    QgsCoordinateReferenceSystem
from qgis.gui import QgisInterface

from .utils import LayerUtils


class CRSSelectionDialog(QDialog):
    def __init__(self, crs_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Coordinate Reference System")
        self.setGeometry(200, 200, 300, 150)

        # Layout setup
        layout = QVBoxLayout(self)

        # Label
        label = QLabel("Choose the CRS for the points:", self)
        layout.addWidget(label)

        # Combo box for selecting CRS
        self.crs_combo = QComboBox(self)
        self.crs_combo.addItems(crs_list)  # Add the CRS options
        layout.addWidget(self.crs_combo)

        # Button to confirm selection
        self.ok_button = QPushButton("OK", self)
        layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.accept)

    def get_selected_crs(self):
        # Return the selected CRS from the combo box
        return self.crs_combo.currentText()


class FlowlineModule:
    iface: QgisInterface
    layer_utils: LayerUtils

    def __init__(self, iface) -> None:
        self.iface = iface
        self.layer_utils = LayerUtils(iface)

    def method(self):
        print("FlowlineModule method called")
        # Call the function to open the file dialog and load the CSV
        self.open_csv_file_dialog()

    def loadCsvAsFlowline(self, csv_file_path, selected_crs):
        # Create a memory layer for storing the points (Point layer, without Z values)
        layer = QgsVectorLayer(f"Point?crs={selected_crs}", "Flowline", "memory")  # Set CRS to selected CRS
        provider = layer.dataProvider()

        # Add a field for the id (no Z value, only X and Y)
        provider.addAttributes([QgsField("id", QVariant.String)])
        layer.updateFields()

        points = []
        with open(csv_file_path, newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                x = float(row['x'])
                y = float(row['y'])
                point = QgsPoint(x, y)  # Create the point with only X and Y
                points.append(point)

        # Create a feature to represent the points
        for i, point in enumerate(points):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPoint(point))  # Use QgsGeometry.fromPoint() for 2D points
            feature.setAttributes([str(i)])  # Set the id for the point feature

            # Add the feature to the layer
            provider.addFeature(feature)

        # Set the CRS based on user selection
        layer.setCrs(QgsCoordinateReferenceSystem(selected_crs))

        # Add the layer to the QGIS project
        QgsProject.instance().addMapLayer(layer)

    def open_csv_file_dialog(self):
        # Open a file dialog to choose a CSV file
        file_path, _ = QFileDialog.getOpenFileName(self.iface.mainWindow(), "Select CSV File", "", "CSV Files (*.csv)")

        if file_path:
            # List of CRS options
            crs_list = [
                "EPSG:4326",  # WGS 84
                "EPSG:3413",  # Example projection (Arctic)
                "EPSG:3857",  # Web Mercator
                "EPSG:25832",  # UTM 32N
                # Add more EPSG codes or names here
            ]

            # Open CRS selection dialog
            dialog = CRSSelectionDialog(crs_list)
            if dialog.exec_() == QDialog.Accepted:
                selected_crs = dialog.get_selected_crs()
                # If a CRS is selected, call loadCsvAsFlowline with the chosen CRS
                self.loadCsvAsFlowline(file_path, selected_crs)