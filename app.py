import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt
from widgets.sensorUI import SensorUI

class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Home Page")

        layout = QVBoxLayout()

        sensor_button = QPushButton("Sensor UI")
        sensor_button.clicked.connect(self.open_sensor_ui)
        layout.addWidget(sensor_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_sensor_ui(self):
        self.sensor_ui = SensorUI()
        self.sensor_ui.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    home_page = HomePage()
    home_page.show()
    sys.exit(app.exec())